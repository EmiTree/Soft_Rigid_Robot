#include "Navigation.h"

Navigation::Navigation(float movementSetpointOffset, float rotationExtraPwm) {
    this->movementSetpointOffset = movementSetpointOffset;
    this->movementHoldOffset = 0.1f;
    this->rotationExtraPwm = rotationExtraPwm;

    movementDurationMs = 500;
    movementReturnDurationMs = 800;
    rotationDurationMs = 1000;

    movementDirection = MovementNone;
    rotationDirection = RotationNone;

    movementEndTime = get_absolute_time();
    movementReturnStartTime = get_absolute_time();
    rotationEndTime = get_absolute_time();
}

float Navigation::getActiveSetpoint(float balanceSetpoint) {
    if (!isMoving()) {
        return balanceSetpoint;
    }

    if (movementDirection == MovementForward) {
        return balanceSetpoint - movementSetpointOffset;
    }

    if (movementDirection == MovementBackward) {
        return balanceSetpoint + movementSetpointOffset;
    }

    if (movementDirection == MovementReturnForward || movementDirection == MovementReturnBackward) {
        absolute_time_t now = get_absolute_time();

        float elapsedMs = absolute_time_diff_us(movementReturnStartTime, now) / 1000.0f;
        float progress = elapsedMs / movementReturnDurationMs;

        if (progress < 0.0f) {
            progress = 0.0f;
        }

        if (progress > 1.0f) {
            progress = 1.0f;
        }

        float remainingOffset = movementHoldOffset + ((movementSetpointOffset - movementHoldOffset) * (1.0f - progress));

        if (movementDirection == MovementReturnForward) {
            return balanceSetpoint - remainingOffset;
        }

        return balanceSetpoint + remainingOffset;
    }

    if (movementDirection == MovementHoldForward) {
        return balanceSetpoint - movementHoldOffset;
    }

    if (movementDirection == MovementHoldBackward) {
        return balanceSetpoint + movementHoldOffset;
    }

    return balanceSetpoint;
}

void Navigation::moveForward() {
    movementDirection = MovementForward;
    movementEndTime = make_timeout_time_ms(movementDurationMs);
}

void Navigation::moveBackward() {
    movementDirection = MovementBackward;
    movementEndTime = make_timeout_time_ms(movementDurationMs);
}

void Navigation::stopMovement() {
    movementDirection = MovementNone;
}

void Navigation::rotateLeft() {
    rotationDirection = RotationLeft;
    rotationEndTime = make_timeout_time_ms(rotationDurationMs);
}

void Navigation::rotateRight() {
    rotationDirection = RotationRight;
    rotationEndTime = make_timeout_time_ms(rotationDurationMs);
}

void Navigation::stopRotation() {
    rotationDirection = RotationNone;
}

void Navigation::applyRotation(float &leftMotorOutput, float &rightMotorOutput) {
    if (!isRotating()) {
        return;
    }

    if (rotationDirection == RotationLeft) {
        leftMotorOutput -= rotationExtraPwm;
        rightMotorOutput += rotationExtraPwm;
    } else if (rotationDirection == RotationRight) {
        leftMotorOutput += rotationExtraPwm;
        rightMotorOutput -= rotationExtraPwm;
    }

    leftMotorOutput = clampPwm(leftMotorOutput);
    rightMotorOutput = clampPwm(rightMotorOutput);
}

void Navigation::setMovementSetpointOffset(float offset) {
    if (offset < 0.0f) {
        offset = -offset;
    }

    movementSetpointOffset = offset;
}

void Navigation::setMovementHoldOffset(float offset) {
    if (offset < 0.0f) {
        offset = -offset;
    }

    movementHoldOffset = offset;
}

void Navigation::setRotationExtraPwm(float extraPwm) {
    if (extraPwm < 0.0f) {
        extraPwm = -extraPwm;
    }

    if (extraPwm > 100.0f) {
        extraPwm = 100.0f;
    }

    rotationExtraPwm = extraPwm;
}

void Navigation::setMovementDurationMs(uint32_t durationMs) {
    movementDurationMs = durationMs;
}

void Navigation::setMovementReturnDurationMs(uint32_t durationMs) {
    movementReturnDurationMs = durationMs;
}

void Navigation::setRotationDurationMs(uint32_t durationMs) {
    rotationDurationMs = durationMs;
}

float Navigation::getMovementSetpointOffset() {
    return movementSetpointOffset;
}

float Navigation::getMovementHoldOffset() {
    return movementHoldOffset;
}

float Navigation::getRotationExtraPwm() {
    return rotationExtraPwm;
}

uint32_t Navigation::getMovementDurationMs() {
    return movementDurationMs;
}

uint32_t Navigation::getMovementReturnDurationMs() {
    return movementReturnDurationMs;
}

uint32_t Navigation::getRotationDurationMs() {
    return rotationDurationMs;
}

bool Navigation::isMoving() {
    if (movementDirection == MovementNone) {
        return false;
    }

    absolute_time_t now = get_absolute_time();

    if (absolute_time_diff_us(now, movementEndTime) <= 0) {
        if (movementDirection == MovementForward) {
            movementDirection = MovementReturnForward;
            movementReturnStartTime = now;
            movementEndTime = make_timeout_time_ms(movementReturnDurationMs);
            return true;
        }

        if (movementDirection == MovementBackward) {
            movementDirection = MovementReturnBackward;
            movementReturnStartTime = now;
            movementEndTime = make_timeout_time_ms(movementReturnDurationMs);
            return true;
        }

        if (movementDirection == MovementReturnForward) {
            movementDirection = MovementHoldForward;
            return true;
        }

        if (movementDirection == MovementReturnBackward) {
            movementDirection = MovementHoldBackward;
            return true;
        }
    }

    return true;
}

bool Navigation::isRotating() {
    if (rotationDirection == RotationNone) {
        return false;
    }

    absolute_time_t now = get_absolute_time();

    if (absolute_time_diff_us(now, rotationEndTime) <= 0) {
        rotationDirection = RotationNone;
        return false;
    }

    return true;
}

float Navigation::clampPwm(float value) {
    if (value > 100.0f) {
        return 100.0f;
    }

    if (value < -100.0f) {
        return -100.0f;
    }

    return value;
}

