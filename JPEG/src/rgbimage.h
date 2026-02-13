/*
 * rgbimage.h
 * 
 * Created on: Sep 9, 2013
 * 			Author: Amir Yazdanbakhsh <a.yazdanbakhsh@gatech.edu>
 * 
 * Modified by Guilherme Saides Serbai on : Nov 17, 2025
 */

#ifndef RGB_IMAGE_H_
#define RGB_IMAGE_H_
#include <stdio.h>
#include "datatype.h"

typedef struct {
   INT16 r;
   INT16 g;
   INT16 b;
} RgbPixel;

typedef struct {
   int w;
   int h;
   RgbPixel** pixels;
   char* meta;
} RgbImage;

void initRgbImage(RgbImage* image);
// int loadRgbImage(const char* fileName, RgbImage* image); // <-- LINHA ANTIGA
int loadRgbImageFromStream(FILE* stream, RgbImage* image);
int saveRgbImageToStream(RgbImage* image, FILE* stream, float scale);
void freeRgbImage(RgbImage* image);

void makeGrayscale(RgbImage* rgbImage);

void readMcuFromRgbImage(RgbImage* srcImage, int x, int y, INT16* data);
void rgbToYcbcr(int r, int g, int b, INT16* y, INT16* cb, INT16* cr);
void readYBlockFromRgbImage(RgbImage* image, int x, int y, INT16* data);
void readCbBlockFromRgbImage(RgbImage* image, int x, int y, INT16* data);
void readCrBlockFromRgbImage(RgbImage* image, int x, int y, INT16* data);

#endif /* RGB_IMAGE_H_ */
