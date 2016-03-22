#include "Person.h"
#include <vector>
#include <fstream>
#include "TRandom3.h"
#include "TH1.h"
#include "TFile.h"
#include <iostream>
#include <cmath>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string>

int init();
void increaseage();
int havebabies(int);
int forcebabies(int);
int smoothbabies(int,int);
void marry();
void forcemarry();
void death();
float manmarry(float);
float womanmarry(float);
float fertile(float);
float guessdeath();
void printAncestors(Person*);

int mCouples;
