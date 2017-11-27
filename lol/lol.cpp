// lol.cpp: 定义 DLL 应用程序的导出函数。
//
#include "stdafx.h"

#define DLLEXPORT extern "C" __declspec(dllexport)
DLLEXPORT void matchtemplate(int* , int , int , int , unsigned char* , int , int , float * );

void matchtemplate(int* xys, int len_xys,int height,int width, unsigned char* frame,int height_frame,int width_frame,float * result)
{
	int t = len_xys;
	int x;
	int y;
	int i;
	int cnt;
	int x_max=0;
	int y_max=0;
	int max = 0;
	for (x = 0;x <= height_frame - height;x++)
	{
		for (y = 0;y <= width_frame - width;y++)
		{
			cnt = 0;
			for (i = 0;i < len_xys;i++)
			{
				if (frame[(x + xys[i * 2])*width_frame + (y + xys[i * 2 + 1])] == 1)
					cnt++;
			}
			if (cnt > max)
			{
				max = cnt;
				x_max = x;
				y_max = y;
			}
		}
	}
	result[0] = float(max) / t;
	result[1] = x_max;
	result[2] = y_max;
}

