from tensorflow.examples.tutorials.mnist import input_data
#mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
import tensorflow as tf
import os
import numpy as np
from PIL import Image

# 第一次遍历图片目录是为了获取图片总数
input_count = 0
for i in range(0, 10):
    dir = './djfb_mnist_digits_images/%s/' % i  # 这里可以改成你自己的图片目录，i为分类标签
    for rt, dirs, files in os.walk(dir):
        for filename in files:
            input_count += 1
            # 定义对应维数和各维长度的数组
input_images = np.array([[0] * 784 for i in range(input_count)])
input_labels = np.array([[0] * 10 for i in range(input_count)])

# 第二次遍历图片目录是为了生成图片数据和标签
index = 0
for i in range(0, 10):
    dir = './djfb_mnist_digits_images/%s/' % i  # 这里可以改成你自己的图片目录，i为分类标签
    for rt, dirs, files in os.walk(dir):
        for filename in files:
            filename = dir + filename
            img = Image.open(filename)
            width = img.size[0]
            height = img.size[1]
            for h in range(0, height):
                for w in range(0, width):
                    # 通过这样的处理，使数字的线条变细，有利于提高识别准确率
                    if img.getpixel((w, h)) > 230:
                        input_images[index][w + h * width] = 0
                    else:
                        input_images[index][w + h * width] = 1
            input_labels[index][i] = 1
            index += 1





sess = tf.InteractiveSession()


x = tf.placeholder(tf.float32, shape=[None, 784])
y_ = tf.placeholder(tf.float32, shape=[None, 10])
W = tf.Variable(tf.zeros([784,10]))
b = tf.Variable(tf.zeros([10]))


sess.run(tf.global_variables_initializer())


def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME')

W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])
x_image = tf.reshape(x, [-1,28,28,1])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

y_conv = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
cross_entropy = tf.reduce_mean(
    tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

saver = tf.train.Saver()  # defaults to saving all variables

sess.run(tf.global_variables_initializer())


print("一共读取了 %s 个输入图像， %s 个标签" % (input_count, input_count))
# 设置每次训练op的输入个数和迭代次数，这里为了支持任意图片总数，定义了一个余数remainder，譬如，如果每次训练op的输入个数为60，图片总数为150张，则前面两次各输入60张，最后一次输入30张（余数30）
batch_size = 60
iterations = 50
batches_count = int(input_count / batch_size)
remainder = input_count % batch_size
print("数据集分成 %s 批, 前面每批 %s 个数据，最后一批 %s 个数据" % (batches_count + 1, batch_size, remainder))

# 执行训练迭代
for it in range(iterations):
    print("执行迭代{}".format(iterations))
    # 这里的关键是要把输入数组转为np.array
    for n in range(batches_count):
        train_step.run(feed_dict={x: input_images[n*batch_size:(n+1)*batch_size], y_: input_labels[n*batch_size:(n+1)*batch_size], keep_prob: 0.5})
    if remainder > 0:
        start_index = batches_count * batch_size
        train_step.run(feed_dict={x: input_images[start_index:input_count-1], y_: input_labels[start_index:input_count-1], keep_prob: 0.5})

    # 每完成五次迭代，判断准确度是否已达到100%，达到则退出迭代循环
    iterate_accuracy = 0
    if it%5 == 0:
        iterate_accuracy = accuracy.eval(feed_dict={x: input_images, y_: input_labels, keep_prob: 1.0})
        print ('iteration %d: accuracy %s' % (it, iterate_accuracy))
        if iterate_accuracy >= 1:
            break

saver.save(sess, 'D:/model.ckpt')  #保存模型参数，注意把这里改为自己的路径