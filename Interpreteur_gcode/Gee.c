#include <stdio.h>
#include <time.h>
#include <pigpio.h>
#include <unistd.h>
#include <math.h>
#include <pthread.h>
#include <semaphore.h>
#include "Gee.h"
#include <stdlib.h>
#include <string.h>

void *motorControl(void *args) {

    struct ThreadArgs *threadArgs = (struct ThreadArgs *)args;

    int nb_Steps = threadArgs->nb_Steps;
    printf("\nnb_Steps = %d \n", nb_Steps);
    int direction = threadArgs->direction;
    char axis = threadArgs->axis;
    Machine m = threadArgs->enrouleuse;
    sem_t *semaphore = threadArgs->semaphore;

    int pulse_Pin;
    int dir_Pin;
    float pulse_Per_Rev;
    float speed = (threadArgs->currentInstruction.F);
    float circumference;
    double poly = -0.00064926513815402706*threadArgs->currentInstruction.S*threadArgs->currentInstruction.S + 0.72272486772486777*threadArgs->currentInstruction.S + 16.713571428571427;
    //double tempspeed;

     switch(axis) {
        case 'A':
            pulse_Pin = m.pulse_A;
            dir_Pin = m.pin_Dir_A;
            pulse_Per_Rev = m.PPR_A;
            //tempspeed = threadArgs->currentInstruction.S/75;
            //speed = threadArgs->currentInstruction.S*(8.5 / (-0.00126984126984126984*threadArgs->currentInstruction.S*threadArgs->currentInstruction.S+1.4555555555*threadArgs->currentInstruction.S+32.357142857142861));
            speed = threadArgs->currentInstruction.S*(8.5); 
            printf("oldspeed = %f\n", speed);
            printf("newspeed factor = %f\n", (poly/threadArgs->currentInstruction.S));
            //
            speed = (threadArgs->currentInstruction.S/(poly/threadArgs->currentInstruction.S))*(8.5);
            //
            printf("newspeed = %f\n", speed);
            //speed = threadArgs->currentInstruction.S*8.5*pow(1.25, tempspeed);
            //speed = threadArgs->currentInstruction.S*8.5*1.25*tempspeed;
            circumference = 360;
            break;
        case 'B':
            pulse_Pin = m.pulse_B;
            dir_Pin = m.pin_Dir_B;
            pulse_Per_Rev = m.PPR_B;
            circumference = roundf(M_PI*m.dB);
            break;
        case 'C':
            pulse_Pin = m.pulse_C;
            dir_Pin = m.pin_Dir_C;
            pulse_Per_Rev = m.PPR_C;
            circumference = 360;
            break;
        case 'D':
            pulse_Pin = m.pulse_D;
            dir_Pin = m.pin_Dir_D;
            pulse_Per_Rev = m.PPR_D;
            circumference = roundf(M_PI*m.dD);
            break;    
        default:
            printf("Invalid choice\n");
            break;
    }

    long start_time, current_time;
    double nsec;

    float waiting_Time = roundf((circumference/speed)/pulse_Per_Rev*1000000-pulse_time);

    printf("Axis : %c runs with a waiting_Time of : %f\n", axis, waiting_Time);

    if (direction == 0) {
        gpioWrite(dir_Pin, PI_HIGH);
    } else if (direction == 1){
        gpioWrite(dir_Pin, PI_LOW);
    }

    usleep(8);

    for (int i=0; i<nb_Steps; i++) {
        gpioWrite(pulse_Pin, PI_HIGH);
        usleep(pulse_time);
        gpioWrite(pulse_Pin, PI_LOW);
        usleep(waiting_Time);
    }
}

Machine loadParameters() {
    Machine m;

    FILE *file;
    float number[100];
    int count=0;

    file = fopen("parameters.conf", "r");

    if (file == NULL) {
        printf("Unable to load parameters!\n");
    }

    while (fscanf(file, "%f", &number[count]) == 1 && count < 100) {
        count++;
    }

    fclose(file);

    m.PPR_A = number[0];
    m.PPR_B = number[1];
    m.PPR_C = number[2];
    m.PPR_D = number[3];
    m.PPR_E = number[4];
    m.pulse_A = number[5];
    m.pulse_B = number[6];
    m.pulse_C = number[7];
    m.pulse_D = number[8];
    m.pulse_E = number[9];
    m.pin_Dir_A = number[10];
    m.pin_Dir_B = number[11];
    m.pin_Dir_C = number[12];
    m.pin_Dir_D = number[13];
    m.pin_Dir_E = number[14];
    m.dA = number[23];
    m.dB = number[24];
    m.dC = number[25];
    m.dD = number[26];
    m.dE = number[27];

    return m;
}

void initialisePi(Machine Enrouleuse) {
    gpioInitialise();
    gpioSetMode(Enrouleuse.pulse_A, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pin_Dir_A, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pulse_B, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pin_Dir_B, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pulse_C, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pin_Dir_C, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pulse_D, PI_OUTPUT);
    gpioSetMode(Enrouleuse.pin_Dir_D, PI_OUTPUT);

/*
    gpioSetMode(Enrouleuse.start_B, PI_INPUT);
    gpioSetMode(Enrouleuse.end_B, PI_INPUT);
    gpioSetMode(Enrouleuse.start_C, PI_INPUT);
    gpioSetMode(Enrouleuse.end_C, PI_INPUT);
    gpioSetMode(Enrouleuse.start_D, PI_INPUT);
    gpioSetMode(Enrouleuse.end_D, PI_INPUT);
    */
}

FILE *loadInstruction(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening G-Code file");
        exit(EXIT_FAILURE);
    }
    return file;
}

void parseLine(const char *line, Instruction *instr) {

        char letter;
        float value;

        printf("%s\n", line);

        // Scan each character of the line
        while (sscanf(line, " %c%f", &letter, &value) == 2) {
            // Depending on the letter, assign the value to the corresponding field in the instruction
            switch (letter) {
                case 'A':
                    instr->A = value;
                    break;
                case 'B':
                    instr->B = value;
                    break;
                case 'C':
                    instr->C = value;
                    break;
                case 'D':
                    instr->D = value;
                    break;
                case 'E':
                    instr->E = value;
                    break;
                case 'F':
                    instr->F = value;
                    break;
                case 'G':
                    instr->G = (unsigned int)value;
                    break;
                case 'H':
                    instr->H = value;
                    break;
                case 'I':
                    instr->I = value;
                    break;
                case 'J':
                    instr->J = value;
                    break;
                case 'K':
                    instr->K = value;
                    break;
                case 'L':
                    instr->L = value;
                    break;
                case 'M':
                    instr->M = (unsigned int)value;
                    break;
                case 'N':
                    instr->N = (unsigned long)value;
                    break;
                case 'O':
                    instr->O = value;
                    break;
                case 'P':
                    instr->P = (unsigned int)value;
                    break;
                case 'S':
                    instr->S = value;
                    break;
                default:
                    break;
            }
        // Move to the next space-separated token
        line = strchr(line, ' ');
        if (line == NULL) break;
        line++;
    }
}

void translateInstruction(Instruction inst1, Instruction inst2, Machine Enrouleuse) {
    float diff_A = inst1.A - inst2.A;
    float diff_B = inst1.B - inst2.B;
    float diff_C = inst1.C - inst2.C;
    float diff_D = inst1.D - inst2.D;
    float diff_E = inst1.E - inst2.E;

    printf("\ndiffA = %f\n", diff_A);

    dir_A = (diff_A > 0) ? 0 : 1;
    dir_B = (diff_B > 0) ? 0 : 1;
    dir_C = (diff_C > 0) ? 0 : 1;
    dir_D = (diff_D > 0) ? 0 : 1;
    dir_E = (diff_E > 0) ? 0 : 1;

    nb_Steps_A = roundf(8.5*(Enrouleuse.PPR_A/360*abs(diff_A)));
    printf("\ntransA = %d\n", nb_Steps_A);
    nb_Steps_B = roundf(abs(diff_B)*Enrouleuse.PPR_B/(Enrouleuse.dB*M_PI));
    nb_Steps_C = roundf(abs(diff_C)*Enrouleuse.PPR_C/(Enrouleuse.dC*M_PI));
    nb_Steps_D = roundf(4*Enrouleuse.PPR_D/360*abs(diff_D));
    nb_Steps_E = roundf(abs(diff_E)*Enrouleuse.PPR_E/(Enrouleuse.dE*M_PI));

}

Instruction newInstruction() {
    Instruction i;
    i.A = 0;
    i.B = 0;
    i.C = 0;
    i.D = 0;
    i.E = 0;
    i.F = 0;
    i.G = 0;
    i.H = 0;
    i.I = 0;
    i.J = 0;
    i.K = 0;
    i.L = 0;
    i.M = 0;
    i.N = 0;
    i.O = 0;
    i.P = 0;
    i.S = 0;
    return i;
}

void copyInstruction(Instruction *dest, Instruction *src) {
    dest->A = src->A;
    dest->B = src->B;
    dest->C = src->C;
    dest->D = src->D;
    dest->E = src->E;
    dest->F = src->F;
    dest->G = src->G;
    dest->H = src->H;
    dest->I = src->I;
    dest->J = src->J;
    dest->K = src->K;
    dest->L = src->L;
    dest->M = src->M;
    dest->N = src->N;
    dest->O = src->O;
    dest->P = src->P;
    dest->S = src->S;
}


int main() {
    Machine Enrouleuse = loadParameters();
    initialisePi(Enrouleuse);

    char filename[100];
    printf("Specify the G-Code file name (case sensitive) :\n");
    scanf("%s", filename);

    FILE *file = loadInstruction(filename);
    char line[256];

    Instruction oldInstruction = newInstruction();
    Instruction currentInstruction = newInstruction();

    sem_t sem_AxisA, sem_AxisB, sem_AxisC, sem_AxisD;
    sem_init(&sem_AxisA, 0, 1);
    sem_init(&sem_AxisB, 0, 1);
    sem_init(&sem_AxisC, 0, 1);
    sem_init(&sem_AxisD, 0, 1);
    pthread_t threadA, threadB, threadC, threadD;

        while (fgets(line, sizeof(line), file)) {
            if (line[0] == '/' || line[0] == '#' || line[0] == '\r' || line[0] == '\n') continue;

            parseLine(line, &currentInstruction);

            translateInstruction(currentInstruction, oldInstruction, Enrouleuse);

            struct ThreadArgs motorA = {nb_Steps_A, dir_A, 'A', Enrouleuse, currentInstruction, &sem_AxisA};
            printf("\nnb_steps de A = %d\n", nb_Steps_A);
            struct ThreadArgs motorB = {nb_Steps_B, dir_B, 'B', Enrouleuse, currentInstruction, &sem_AxisB};
            struct ThreadArgs motorC = {nb_Steps_C, dir_C, 'C', Enrouleuse, currentInstruction, &sem_AxisC};
            struct ThreadArgs motorD = {nb_Steps_D, dir_D, 'D', Enrouleuse, currentInstruction, &sem_AxisD};

            pthread_create(&threadA, NULL, motorControl, (void *)&motorA);
            pthread_create(&threadB, NULL, motorControl, (void *)&motorB);
            pthread_create(&threadC, NULL, motorControl, (void *)&motorC);
            pthread_create(&threadD, NULL, motorControl, (void *)&motorD);
        
            pthread_join(threadA, NULL);
            pthread_join(threadB, NULL);
            pthread_join(threadC, NULL);
            pthread_join(threadD, NULL); 

            sem_destroy(&sem_AxisA);
            sem_destroy(&sem_AxisB);
            sem_destroy(&sem_AxisC);
            sem_destroy(&sem_AxisD);

            copyInstruction(&oldInstruction, &currentInstruction);

        }

    gpioTerminate();
    return 0;
};


//Note to self : le brin fait 10mm de large une fois roulé
// Il faute que le mandrin pousse plus 
//Ajoute cette putain de vitesse pour le mandrin