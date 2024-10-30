#ifndef GEE_H
#define GEE_H

int dir_A;
int dir_B;
int dir_C;
int dir_D;
int dir_E;

int nb_Steps_A;
int nb_Steps_B;
int nb_Steps_C;
int nb_Steps_D;
int nb_Steps_E;

int pulse_time = 8;

typedef struct{
    float A;
    float B;
    float C;
    float D;
    float E;
    float F;
    unsigned int G;
    float H;
    float I;
    float J;
    float K;
    float L;
    unsigned int M;
    unsigned long int N;
    float O;
    unsigned int P;
    float S;
}Instruction;

typedef struct{
    float PPR_A;
    float PPR_B;
    float PPR_C;
    float PPR_D;
    float PPR_E;
    int pulse_A;
    int pulse_B;
    int pulse_C;
    int pulse_D;
    int pulse_E;
    int pin_Dir_A;
    int pin_Dir_B;
    int pin_Dir_C;
    int pin_Dir_D;
    int pin_Dir_E;
    int start_A;
    int end_A;
    int start_B;
    int end_B;
    int start_C;
    int end_C;
    int start_D;
    int end_D;
    float dA;
    float dB;
    float dC;
    float dD;
    float dE;
}Machine;

struct ThreadArgs {
    int nb_Steps;
    int direction;
    char axis;
    Machine enrouleuse;
    Instruction currentInstruction;
    sem_t *semaphore;
};

void copyInstruction(Instruction *dest, Instruction *src);

#endif
