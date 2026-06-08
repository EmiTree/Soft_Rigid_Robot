#pragma once

#include "pico/stdlib.h"

class Navigation {
public:
    Navigation(float movementSetpointOffset, float rotationExtraPwm);

    float getActiveSetpoint(float balanceSetpoint);

    void moveForward();
    void moveBackward();
    void stopMovement();

    void rotateLeft();
    void rotateRight();
    void stopRotation();

    void applyRotation(float &leftMotorOutput, float &rightMotorOutput);

    void setMovementSetpointOffset(float offset);
    void setRotationExtraPwm(float extraPwm);
    void setMovementDurationMs(uint32_t durationMs);
    void setRotationDurationMs(uint32_t durationMs);

    float getMovementSetpointOffset();
    float getRotationExtraPwm();
    uint32_t getMovementDurationMs();
    uint32_t getRotationDurationMs();

    bool isMoving();
    bool isRotating();

private:
    enum MovementDirection {
        MovementNone,
        MovementForward,
        MovementBackward
    };

    enum RotationDirection {
        RotationNone,
        RotationLeft,
        RotationRight
    };

    float movementSetpointOffset;
    float rotationExtraPwm;

    uint32_t movementDurationMs;
    uint32_t rotationDurationMs;

    MovementDirection movementDirection;
    RotationDirection rotationDirection;

    absolute_time_t movementEndTime;
    absolute_time_t rotationEndTime;

    float clampPwm(float value);
};