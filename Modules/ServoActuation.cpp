#include "ServoActuation.h"

#include "hardware/pwm.h"

/*
    PWM setup:
    Pico clock = 125 MHz.
    clkdiv 125 makes PWM tick at 1 MHz, so 1 tick = 1 microsecond.
    wrap 19999 gives a 20 ms servo period.
*/
const int PWM_WRAP = 20000 - 1;

const int SERVO_MIN_US = 1000;
const int SERVO_STOP_US = 1500;
const int SERVO_MAX_US = 2000;

const float SERVO_MIN_SPEED = -100.0f;
const float SERVO_MAX_SPEED = 100.0f;


ServoActuation::ServoActuation(int servo1Pin, int servo2Pin, int servo3Pin, int servo4Pin)
    : servoPins{servo1Pin, servo2Pin, servo3Pin, servo4Pin},
      currentSpeeds{0.0f, 0.0f, 0.0f, 0.0f},
      timedMoveActive{false, false, false, false},
      timedMoveEndTimes{
          get_absolute_time(),
          get_absolute_time(),
          get_absolute_time(),
          get_absolute_time()
      } {
}

void ServoActuation::begin() {
    for (int i = 0; i < ServoCount; i++) {
        setupServoPwm(servoPins[i]);

        currentSpeeds[i] = 0.0f;
        timedMoveActive[i] = false;

        // Stop pulse, so the servo does not start moving during setup.
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

    // Manual speed control cancels a timed move for this servo.
    timedMoveActive[servoIndex] = false;

    writeServoPulse(servoIndex, speedPercent);

    return true;
}

bool ServoActuation::runFor(int servoNumber, float speedPercent, uint32_t durationMs) {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return false;
    }

    startTimedMoveByIndex(servoIndex, speedPercent, durationMs);
    return true;
}

bool ServoActuation::runMoves(const ServoMove moves[], int moveCount) {
    if (moves == nullptr || moveCount <= 0) {
        return false;
    }

    // First check every servo number, so a wrong move does not partly start.
    for (int i = 0; i < moveCount; i++) {
        int servoIndex = 0;

        if (!servoNumberToIndex(moves[i].servoNumber, servoIndex)) {
            return false;
        }
    }

    for (int i = 0; i < moveCount; i++) {
        int servoIndex = 0;
        servoNumberToIndex(moves[i].servoNumber, servoIndex);

        startTimedMoveByIndex(
            servoIndex,
            moves[i].speedPercent,
            moves[i].durationMs
        );
    }

    return true;
}

bool ServoActuation::runFour(
    float servo1Speed, uint32_t servo1DurationMs,
    float servo2Speed, uint32_t servo2DurationMs,
    float servo3Speed, uint32_t servo3DurationMs,
    float servo4Speed, uint32_t servo4DurationMs
) {
    ServoMove moves[ServoCount] = {
        {1, servo1Speed, servo1DurationMs},
        {2, servo2Speed, servo2DurationMs},
        {3, servo3Speed, servo3DurationMs},
        {4, servo4Speed, servo4DurationMs}
    };

    return runMoves(moves, ServoCount);
}

bool ServoActuation::runExamplePattern() {
    ServoMove moves[ServoCount] = {
        {1, 5.0f, 3000},
        {2, 2.0f, 2000},
        {3, 7.0f, 6000},
        {4, 2.0f, 4000}
    };

    return runMoves(moves, ServoCount);
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
        // Stop only the servo whose own timer is finished.
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

bool ServoActuation::isTimedMoveActive(int servoNumber) const {
    int servoIndex = 0;

    if (!servoNumberToIndex(servoNumber, servoIndex)) {
        return false;
    }

    return timedMoveActive[servoIndex];
}

bool ServoActuation::anyTimedMoveActive() const {
    for (int i = 0; i < ServoCount; i++) {
        if (timedMoveActive[i]) {
            return true;
        }
    }

    return false;
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
    if (servoIndex < 0 || servoIndex >= ServoCount) {
        return;
    }

    pwm_set_gpio_level(servoPins[servoIndex], speedToPulseUs(speedPercent));
}

void ServoActuation::startTimedMoveByIndex(int servoIndex, float speedPercent, uint32_t durationMs) {
    speedPercent = clampSpeed(speedPercent);

    currentSpeeds[servoIndex] = speedPercent;
    timedMoveActive[servoIndex] = true;
    timedMoveEndTimes[servoIndex] = make_timeout_time_ms(durationMs);

    writeServoPulse(servoIndex, speedPercent);
}

int ServoActuation::speedToPulseUs(float speedPercent) const {
    speedPercent = clampSpeed(speedPercent);

    // -100% -> 1000 us, 0% -> 1500 us, +100% -> 2000 us.
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

// programMovement [[servo1, speed , time], [2] ,[3]
// start making movements here. Example movement1 is added to the header file. You can call it from main to test it, or make your own movements.
bool ServoActuation::movement1() {
    ServoMove moves[ServoCount] = {
        {1, 5.0f, 3000},  // Servo 1: speed +5 for 3 seconds
        {2, 2.0f, 2000},  // Servo 2: speed +2 for 2 seconds
        {3, 7.0f, 6000},  // Servo 3: speed +7 for 6 seconds
        {4, 2.0f, 4000}   // Servo 4: speed +2 for 4 seconds
    };

    return runMoves(moves, ServoCount);
}