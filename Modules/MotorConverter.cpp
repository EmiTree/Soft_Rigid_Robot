#include "MotorConverter.h"

#include <stdio.h>
#include <math.h>

MotorConverter::MotorConverter(float pidOutputLimit, float maxPwm, float motorStartPwm) {
    this->pidOutputLimit = pidOutputLimit;
    this->maxPwm = maxPwm;
    this->leftMotorStartPwm = motorStartPwm;
    this->rightMotorStartPwm = motorStartPwm;

    /*
        Default extra behavior.

        Deadband is on by default to prevent tiny PID outputs from immediately
        giving the motors start power.

        Response curve is off by default because 1.0 is the normal linear
        behavior.
    */
    deadband = 0.0f;
    responseCurve = 1.0f;

    deadbandEnabled = true;
    responseCurveEnabled = false;
}

float MotorConverter::clampFloat(float value, float low, float high) {
    if (value < low) return low;
    if (value > high) return high;
    return value;
}

MotorCommand MotorConverter::convert(float pidOutput) {
    MotorCommand command;

    command.pwmA = 0.0f;
    command.pwmB = 0.0f;
    command.motorOutput = 0.0f;
    command.normalizedOutput = 0.0f;
    command.scaledOutput = 0.0f;
    command.leftMotorOutput = 0.0f;
    command.rightMotorOutput = 0.0f;

    float safePidOutputLimit = clampFloat(pidOutputLimit, 1.0f, 1000.0f);
    float safeMaxPwm = clampFloat(maxPwm, 0.0f, 100.0f);

    float safeLeftMotorStartPwm = clampFloat(leftMotorStartPwm, 0.0f, safeMaxPwm);
    float safeRightMotorStartPwm = clampFloat(rightMotorStartPwm, 0.0f, safeMaxPwm);

    float availableLeftPwmRange = safeMaxPwm - safeLeftMotorStartPwm;
    float availableRightPwmRange = safeMaxPwm - safeRightMotorStartPwm;

    if (availableLeftPwmRange <= 0.0f && availableRightPwmRange <= 0.0f) {
        return command;
    }

    float normalized = pidOutput / safePidOutputLimit;
    normalized = clampFloat(normalized, -1.0f, 1.0f);

    command.normalizedOutput = normalized;

    float direction = 1.0f;

    if (normalized < 0.0f) {
        direction = -1.0f;
    }

    float effort = normalized;

    if (effort < 0.0f) {
        effort = -effort;
    }

    if (deadbandEnabled) {
        float safeDeadband = clampFloat(deadband, 0.0f, 0.95f);

        if (effort < safeDeadband) {
            return command;
        }

        effort = (effort - safeDeadband) / (1.0f - safeDeadband);
    }

    effort = clampFloat(effort, 0.0f, 1.0f);

    if (responseCurveEnabled) {
        float safeCurve = clampFloat(responseCurve, 0.1f, 5.0f);
        effort = powf(effort, safeCurve);
    }

    command.scaledOutput = effort;

    float leftPwm = safeLeftMotorStartPwm + effort * availableLeftPwmRange;
    float rightPwm = safeRightMotorStartPwm + effort * availableRightPwmRange;

    leftPwm = clampFloat(leftPwm, 0.0f, safeMaxPwm);
    rightPwm = clampFloat(rightPwm, 0.0f, safeMaxPwm);

    command.leftMotorOutput = direction * leftPwm;
    command.rightMotorOutput = direction * rightPwm;

    command.motorOutput = direction * ((leftPwm + rightPwm) / 2.0f);

    if (direction > 0.0f) {
        command.pwmA = command.motorOutput;
        command.pwmB = 0.0f;
    } else {
        command.pwmA = 0.0f;
        command.pwmB = -command.motorOutput;
    }

    return command;
}

void MotorConverter::setPidOutputLimit(float value) {
    pidOutputLimit = clampFloat(value, 1.0f, 1000.0f);
}

void MotorConverter::setMaxPwm(float value) {
    maxPwm = clampFloat(value, 0.0f, 100.0f);

    if (leftMotorStartPwm > maxPwm) {
        leftMotorStartPwm = maxPwm;
    }

    if (rightMotorStartPwm > maxPwm) {
        rightMotorStartPwm = maxPwm;
    }
}

void MotorConverter::setMotorStartPwm(float value) {
    leftMotorStartPwm = clampFloat(value, 0.0f, maxPwm);
    rightMotorStartPwm = clampFloat(value, 0.0f, maxPwm);
}

void MotorConverter::setLeftMotorStartPwm(float value) {
    leftMotorStartPwm = clampFloat(value, 0.0f, maxPwm);
}

void MotorConverter::setRightMotorStartPwm(float value) {
    rightMotorStartPwm = clampFloat(value, 0.0f, maxPwm);
}

void MotorConverter::setDeadband(float value) {
    deadband = clampFloat(value, 0.0f, 0.95f); 
}

void MotorConverter::setResponseCurve(float value) {
    responseCurve = clampFloat(value, 0.1f, 5.0f);
}

void MotorConverter::setDeadbandEnabled(bool enabled) {
    deadbandEnabled = enabled;
}

void MotorConverter::setResponseCurveEnabled(bool enabled) {
    responseCurveEnabled = enabled;
}

float MotorConverter::getPidOutputLimit() {
    return pidOutputLimit;
}

float MotorConverter::getMaxPwm() {
    return maxPwm;
}

float MotorConverter::getMotorStartPwm() {
    return (leftMotorStartPwm + rightMotorStartPwm) / 2.0f;
}

float MotorConverter::getLeftMotorStartPwm() {
    return leftMotorStartPwm;
}

float MotorConverter::getRightMotorStartPwm() {
    return rightMotorStartPwm;
}

float MotorConverter::getDeadband() {
    return deadband;
}

float MotorConverter::getResponseCurve() {
    return responseCurve;
}

bool MotorConverter::isDeadbandEnabled() {
    return deadbandEnabled;
}

bool MotorConverter::isResponseCurveEnabled() {
    return responseCurveEnabled;
}

void MotorConverter::printSettings() {
    printf("\nMotor converter settings:\n");
    printf("pidOutputLimit = %.2f\n", pidOutputLimit);
    printf("maxPwm = %.2f\n", maxPwm);
    printf("leftMotorStartPwm = %.2f\n", leftMotorStartPwm);
    printf("rightMotorStartPwm = %.2f\n", rightMotorStartPwm);
    printf("deadband = %.4f\n", deadband);
    printf("deadbandEnabled = %d\n", deadbandEnabled);
    printf("responseCurve = %.4f\n", responseCurve);
    printf("responseCurveEnabled = %d\n\n", responseCurveEnabled);
}