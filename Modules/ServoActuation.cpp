#include "ServoActuation.h"

#include "hardware/pwm.h"

/*
    PWM setup:
    The Pico runs at 125 MHz.
    With clkdiv 125, the PWM clock becomes 1 MHz.
    That means 1 PWM tick = 1 microsecond.

    With wrap = 19999, the PWM period is 20000 us = 20 ms.
    This is the standard servo refresh period.
*/
const int PWM_WRAP = 20000 - 1;

/*
    Continuous-rotation servo pulse widths:
        1000 us = full speed one direction
        1500 us = stop
        2000 us = full speed the other direction
*/
const int SERVO_MIN_US = 1000;
const int SERVO_STOP_US = 1500;
const int SERVO_MAX_US = 2000;

const float SERVO_MIN_SPEED = -100.0f;
const float SERVO_MAX_SPEED = 100.0f;

ServoActuation::ServoActuation(int servo1Pin, int servo2Pin, int servo3Pin, int servo4Pin)
    : servoPins{servo1Pin, servo2Pin, servo3Pin, servo4Pin},
      currentSpeeds{0.0f, 0.0f, 0.0f, 0.0f},
      timedMoveActive{false, false, false, false}, 
      timedMoveEndTimes{get_absolute_time(), get_absolute_time(), get_absolute_time(), get_absolute_time()} {
}

void ServoActuation::begin() {
    for (int i = 0; i < ServoCount; i++) { // Loop through each servo pin and set it up for PWM output.
        setupServoPwm(servoPins[i]); 

        currentSpeeds[i] = 0.0f; 
        timedMoveActive[i] = false; // Make sure all timed move states are reset.

        // Send stop pulse after setup so the servo does not start moving.
        writeServoPulse(i, 0.0f);
    }
}

bool ServoActuation::setSpeed(int servoNumber, float speedPercent) {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return false;
    }

    speedPercent = clampSpeed(speedPercent);

    currentSpeeds[servoIndex] = speedPercent;

    // A manual speed command cancels any timed move for this servo.
    timedMoveActive[servoIndex] = false;

    writeServoPulse(servoIndex, speedPercent);

    return true;
}

bool ServoActuation::runFor(int servoNumber, float speedPercent, uint32_t durationMs) {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return false;
    }

    speedPercent = clampSpeed(speedPercent);

    currentSpeeds[servoIndex] = speedPercent;
    timedMoveActive[servoIndex] = true;
    timedMoveEndTimes[servoIndex] = make_timeout_time_ms(durationMs);

    writeServoPulse(servoIndex, speedPercent);

    return true;
}

void ServoActuation::stop(int servoNumber) {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return;
    }

    currentSpeeds[servoIndex] = 0.0f;
    timedMoveActive[servoIndex] = false;

    writeServoPulse(servoIndex, 0.0f);
}

void ServoActuation::stopAll() {
    for (int i = 0; i < ServoCount; i++) {
        currentSpeeds[i] = 0.0f;
        timedMoveActive[i] = false;

        writeServoPulse(i, 0.0f);
    }
}

void ServoActuation::update() {
    absolute_time_t now = get_absolute_time();

    for (int i = 0; i < ServoCount; i++) {
        // If a timed move is active and the end time has passed, stop that servo.
        if (timedMoveActive[i] && absolute_time_diff_us(now, timedMoveEndTimes[i]) <= 0) {
            currentSpeeds[i] = 0.0f;
            timedMoveActive[i] = false;

            writeServoPulse(i, 0.0f);
        }
    }
}

float ServoActuation::getSpeed(int servoNumber) const {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return 0.0f;
    }

    return currentSpeeds[servoIndex];
}

bool ServoActuation::isRunning(int servoNumber) const {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return false;
    }

    return currentSpeeds[servoIndex] != 0.0f;
}

void ServoActuation::setupServoPwm(int pin) {
    gpio_set_function(pin, GPIO_FUNC_PWM);

    uint slice = pwm_gpio_to_slice_num(pin);

    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 125.0f);
    pwm_config_set_wrap(&config, PWM_WRAP);

    pwm_init(slice, &config, true);
    pwm_set_gpio_level(pin, SERVO_STOP_US);
}

void ServoActuation::writeServoPulse(int servoIndex, float speedPercent) {
    if (servoIndex >= ServoCount) {
        return;
    }

    pwm_set_gpio_level(servoPins[servoIndex], speedToPulseUs(speedPercent));
}

int ServoActuation::speedToPulseUs(float speedPercent) const {
    speedPercent = clampSpeed(speedPercent);

    /*
        Convert speed percentage to servo pulse:

        -100% -> 1000 us
           0% -> 1500 us
        +100% -> 2000 us
    */
    int pulseUs = SERVO_STOP_US + (int)((speedPercent / 100.0f) * 500.0f);

    if (pulseUs < SERVO_MIN_US) {
        return SERVO_MIN_US;
    }

    if (pulseUs > SERVO_MAX_US) {
        return SERVO_MAX_US;
    }

    return pulseUs;
}

float ServoActuation::clampSpeed(float speedPercent) const {
    if (speedPercent < SERVO_MIN_SPEED) {
        return SERVO_MIN_SPEED;
    }

    if (speedPercent > SERVO_MAX_SPEED) {
        return SERVO_MAX_SPEED;
    }

    return speedPercent;
}

bool ServoActuation::servoNumberToIndex(int servoNumber, int &servoIndex) const {
    if (servoNumber < 1 || servoNumber > ServoCount) {
        return false;
    }

    servoIndex = servoNumber - 1;
    return true;
}