#include "pico/stdlib.h"
#include "hardware/pwm.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const int ServoCount = 4;

// het is of 13

const int SERVO_1_PIN = 18;
const int SERVO_2_PIN = 15;
const int SERVO_3_PIN = 16;
const int SERVO_4_PIN = 17;

const int SERVO_PINS[ServoCount] = {
    SERVO_1_PIN,
    SERVO_2_PIN,
    SERVO_3_PIN,
    SERVO_4_PIN
};

const int PWM_WRAP = 20000 - 1;

const int SERVO_MIN_US = 1000;
const int SERVO_STOP_US = 1500;
const int SERVO_MAX_US = 2000;

const float MIN_SPEED = -100.0f;
const float MAX_SPEED = 100.0f;

struct ServoMove {
    int servoNumber;
    float speedPercent;
    uint32_t durationMs;
};

float Servo1MovementSpeed = 50.0f;
float Servo2MovementSpeed = 50.0f;
float Servo3MovementSpeed = 50.0f;
float Servo4MovementSpeed = 50.0f;

uint32_t Servo1MovementTime = 3000;
uint32_t Servo2MovementTime = 3000;
uint32_t Servo3MovementTime = 3000;
uint32_t Servo4MovementTime = 3000;

float currentSpeeds[ServoCount] = {0.0f, 0.0f, 0.0f, 0.0f};
bool timedMoveActive[ServoCount] = {false, false, false, false};
absolute_time_t timedMoveEndTimes[ServoCount];

char inputBuffer[80];
int inputIndex = 0;
bool hasPendingInput = false;
absolute_time_t lastInputTime;

float clampFloat(float value, float low, float high) {
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

int clampInt(int value, int low, int high) {
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

int speedToPulseUs(float speedPercent) {
    speedPercent = clampFloat(speedPercent, MIN_SPEED, MAX_SPEED);

    int pulseUs = SERVO_STOP_US + (int)((speedPercent / 100.0f) * 500.0f);

    return clampInt(pulseUs, SERVO_MIN_US, SERVO_MAX_US);
}

void setupServoPwm(int pin) {
    gpio_set_function(pin, GPIO_FUNC_PWM);

    uint slice = pwm_gpio_to_slice_num(pin);

    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 125.0f);
    pwm_config_set_wrap(&config, PWM_WRAP);

    pwm_init(slice, &config, true);
    pwm_set_gpio_level(pin, SERVO_STOP_US);

    printf("Setup servo PWM on GP%d\n", pin);
}

void writeServoSpeed(int servoIndex, float speedPercent) {
    if (servoIndex < 0 || servoIndex >= ServoCount) {
        return;
    }

    pwm_set_gpio_level(SERVO_PINS[servoIndex], speedToPulseUs(speedPercent));
}

void stopServoByIndex(int servoIndex) {
    currentSpeeds[servoIndex] = 0.0f;
    timedMoveActive[servoIndex] = false;
    writeServoSpeed(servoIndex, 0.0f);
}

void stopAllServos() {
    for (int i = 0; i < ServoCount; i++) {
        stopServoByIndex(i);
    }

    printf("\nAll servos stopped\n");
}

void runMoves(const ServoMove moves[], int moveCount) {
    for (int i = 0; i < moveCount; i++) {
        int servoIndex = moves[i].servoNumber - 1;

        if (servoIndex < 0 || servoIndex >= ServoCount) {
            printf("\nInvalid servo number: %d\n", moves[i].servoNumber);
            continue;
        }

        float speed = clampFloat(moves[i].speedPercent, MIN_SPEED, MAX_SPEED);

        currentSpeeds[servoIndex] = speed;
        timedMoveActive[servoIndex] = true;
        timedMoveEndTimes[servoIndex] = make_timeout_time_ms(moves[i].durationMs);

        writeServoSpeed(servoIndex, speed);

        printf("Servo %d running at %.1f%% for %lu ms\n",
               moves[i].servoNumber,
               speed,
               moves[i].durationMs);
    }
}

void runCurrentMovement() {
    ServoMove moves[ServoCount] = {
        {1, Servo1MovementSpeed, Servo1MovementTime},
        {2, Servo2MovementSpeed, Servo2MovementTime},
        {3, Servo3MovementSpeed, Servo3MovementTime},
        {4, Servo4MovementSpeed, Servo4MovementTime}
    };

    printf("\nStarting movement\n");
    runMoves(moves, ServoCount);
}

void updateTimedMoves() {
    absolute_time_t now = get_absolute_time();

    for (int i = 0; i < ServoCount; i++) {
        if (timedMoveActive[i] && absolute_time_diff_us(now, timedMoveEndTimes[i]) <= 0) {
            stopServoByIndex(i);
            printf("\nServo %d finished and stopped\n", i + 1);
        }
    }
}

void printStatus() {
    printf("\n--- Servo movement settings ---\n");
    printf("Servo 1 | GP%d | speed %.1f%% | time %.2f seconds | running %.1f%%\n",
           SERVO_1_PIN, Servo1MovementSpeed, Servo1MovementTime / 1000.0f, currentSpeeds[0]);
    printf("Servo 2 | GP%d | speed %.1f%% | time %.2f seconds | running %.1f%%\n",
           SERVO_2_PIN, Servo2MovementSpeed, Servo2MovementTime / 1000.0f, currentSpeeds[1]);
    printf("Servo 3 | GP%d | speed %.1f%% | time %.2f seconds | running %.1f%%\n",
           SERVO_3_PIN, Servo3MovementSpeed, Servo3MovementTime / 1000.0f, currentSpeeds[2]);
    printf("Servo 4 | GP%d | speed %.1f%% | time %.2f seconds | running %.1f%%\n",
           SERVO_4_PIN, Servo4MovementSpeed, Servo4MovementTime / 1000.0f, currentSpeeds[3]);
    printf("-------------------------------\n");
}

void printHelp() {
    printf("\nCommands:\n");
    printf("run                         -> run the current 4-servo movement\n");
    printf("stop                        -> stop all servos\n");
    printf("status                      -> print current settings\n");
    printf("help                        -> print this help text\n");

    printf("\nChange speeds:\n");
    printf("servo1movementspeed +50     -> set servo 1 speed to +50%%\n");
    printf("servo2movementspeed -25     -> set servo 2 speed to -25%%\n");
    printf("servo3movementspeed +10     -> set servo 3 speed to +10%%\n");
    printf("servo4movementspeed 0       -> set servo 4 speed to 0%%\n");

    printf("\nChange times, in seconds:\n");
    printf("servo1movementtime 10       -> set servo 1 time to 10 seconds\n");
    printf("servo2movementtime 2.5      -> set servo 2 time to 2.5 seconds\n");
    printf("servo3movementtime 6        -> set servo 3 time to 6 seconds\n");
    printf("servo4movementtime 4        -> set servo 4 time to 4 seconds\n\n");
}

void clearInputBuffer() {
    for (int i = 0; i < 80; i++) {
        inputBuffer[i] = '\0';
    }

    inputIndex = 0;
    hasPendingInput = false;
}

void setMovementTime(uint32_t &movementTimeMs, float seconds) {
    if (seconds < 0.0f) {
        seconds = 0.0f;
    }

    movementTimeMs = (uint32_t)(seconds * 1000.0f);
}

void processInput() {
    inputBuffer[inputIndex] = '\0';

    if (inputIndex == 0) {
        clearInputBuffer();
        return;
    }

    char command[40];
    float value = 0.0f;

    int parts = sscanf(inputBuffer, "%39s %f", command, &value);

    printf("\nReceived command: %s\n", inputBuffer);

    if (parts >= 1) {
        if (strcmp(command, "run") == 0) {
            runCurrentMovement();

        } else if (strcmp(command, "stop") == 0) {
            stopAllServos();

        } else if (strcmp(command, "status") == 0) {
            printStatus();

        } else if (strcmp(command, "help") == 0) {
            printHelp();

        } else if (strcmp(command, "servo1movementspeed") == 0 && parts == 2) {
            Servo1MovementSpeed = clampFloat(value, MIN_SPEED, MAX_SPEED);
            printf("Servo 1 movement speed set to %.1f%%\n", Servo1MovementSpeed);

        } else if (strcmp(command, "servo2movementspeed") == 0 && parts == 2) {
            Servo2MovementSpeed = clampFloat(value, MIN_SPEED, MAX_SPEED);
            printf("Servo 2 movement speed set to %.1f%%\n", Servo2MovementSpeed);

        } else if (strcmp(command, "servo3movementspeed") == 0 && parts == 2) {
            Servo3MovementSpeed = clampFloat(value, MIN_SPEED, MAX_SPEED);
            printf("Servo 3 movement speed set to %.1f%%\n", Servo3MovementSpeed);

        } else if (strcmp(command, "servo4movementspeed") == 0 && parts == 2) {
            Servo4MovementSpeed = clampFloat(value, MIN_SPEED, MAX_SPEED);
            printf("Servo 4 movement speed set to %.1f%%\n", Servo4MovementSpeed);

        } else if (strcmp(command, "servo1movementtime") == 0 && parts == 2) {
            setMovementTime(Servo1MovementTime, value);
            printf("Servo 1 movement time set to %.2f seconds\n", Servo1MovementTime / 1000.0f);

        } else if (strcmp(command, "servo2movementtime") == 0 && parts == 2) {
            setMovementTime(Servo2MovementTime, value);
            printf("Servo 2 movement time set to %.2f seconds\n", Servo2MovementTime / 1000.0f);

        } else if (strcmp(command, "servo3movementtime") == 0 && parts == 2) {
            setMovementTime(Servo3MovementTime, value);
            printf("Servo 3 movement time set to %.2f seconds\n", Servo3MovementTime / 1000.0f);

        } else if (strcmp(command, "servo4movementtime") == 0 && parts == 2) {
            setMovementTime(Servo4MovementTime, value);
            printf("Servo 4 movement time set to %.2f seconds\n", Servo4MovementTime / 1000.0f);

        } else {
            printf("Unknown command: %s\n", inputBuffer);
            printHelp();
        }
    }

    clearInputBuffer();

    printf("\nEnter command: ");
    fflush(stdout);
}

void handleSerialInput() {
    int ch = getchar_timeout_us(0);

    if (ch == PICO_ERROR_TIMEOUT) {
        if (hasPendingInput) {
            absolute_time_t now = get_absolute_time();
            int64_t timeSinceInput = absolute_time_diff_us(lastInputTime, now);

            if (timeSinceInput > 500000) {
                processInput();
            }
        }

        return;
    }

    if (ch == '\r' || ch == '\n') {
        processInput();
        return;
    }

    if (ch == 8 || ch == 127) {
        if (inputIndex > 0) {
            inputIndex--;
            inputBuffer[inputIndex] = '\0';
        }

        hasPendingInput = true;
        lastInputTime = get_absolute_time();
        return;
    }

    if (inputIndex < 79) {
        inputBuffer[inputIndex] = (char)ch;
        inputIndex++;
        inputBuffer[inputIndex] = '\0';

        hasPendingInput = true;
        lastInputTime = get_absolute_time();

        printf("%c", ch);
        fflush(stdout);
    } else {
        printf("\nInput too long, clearing input\n");
        clearInputBuffer();
        printf("Enter command: ");
        fflush(stdout);
    }
}

int main() {
    stdio_init_all();

    while (!stdio_usb_connected()) {
        sleep_ms(100);
    }

    printf("\nServo movement tuning ready\n");

    for (int i = 0; i < ServoCount; i++) {
        setupServoPwm(SERVO_PINS[i]);
        timedMoveEndTimes[i] = get_absolute_time();
    }

    stopAllServos();
    clearInputBuffer();

    printHelp();
    printStatus();

    printf("\nEnter command: ");
    fflush(stdout);

    while (true) {
        handleSerialInput();
        updateTimedMoves();
        sleep_ms(10);
    }
}