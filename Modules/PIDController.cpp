#include "PIDController.h"

/*
    Constructor.

    This runs when the PIDController object is created.

    The parameter names are also kp, ki, and kd, which are the same names as the
    class variables. Because of that, this-> is used.

    this->kp means:
        the kp variable that belongs to this PIDController object

    kp by itself means:
        the kp parameter passed into the constructor

    this-> use the variable that belongs to this object
*/
PIDController::PIDController(float kp, float ki, float kd) {
    this->kp = kp; //Put the input kp value into this object's kp variable.
    this->ki = ki; //Put the input ki value into this object's ki variable.
    this->kd = kd; //Put the input kd value into this object's kd variable.

    /*
        Start with no old error and no accumulated integral.
    */
    previousError = 0.0f;
    integral = 0.0f;
}

/*
    Calculate the PID output.

    This function is called repeatedly in the main loop while PID is running.
*/
float PIDController::update(
    float setpoint,
    float measuredAngle,
    float measuredAngularVelocity,
    float dt,
    float &pValue,
    float &iValue,
    float &dValue
) {
    float error = setpoint - measuredAngle;

    if (dt > 0.0f) {
        integral += error * dt;

        // Anti-windup clamp. Tune this limit for your robot/tentacle.
        const float integralLimit = 100.0f;
        if (integral > integralLimit) integral = integralLimit;
        if (integral < -integralLimit) integral = -integralLimit;
    }

    float derivative = 0.0f;

    if (dt > 0.0f) {
        // Use gyro angular velocity directly for damping.
        derivative = (error - previousError) / dt;
    }

    pValue = kp * error;
    iValue = ki * integral;
    dValue = kd * derivative;

    previousError = error;

    return pValue + iValue + dValue;
}

/*
    Reset the controller memory.

    This does not change kp, ki, or kd.
    It only clears the stored previous error and integral buildup.
*/

void PIDController::reset() {
    previousError = 0.0f;
    integral = 0.0f;
}

/*
    Set a new proportional gain.

    Bigger Kp usually means stronger reaction to current error.
*/
void PIDController::setKp(float newKp) {
    kp = newKp;
}

/*
    Set a new integral gain.

    Bigger Ki usually means stronger correction for long-lasting error, but too
    much can make the system overshoot or become unstable.
*/
void PIDController::setKi(float newKi) {
    ki = newKi;
}

/*
    Set a new derivative gain.

    Bigger Kd usually means stronger damping, because it reacts to fast changes.
    Too much can make the motor response noisy or twitchy.
*/
void PIDController::setKd(float newKd) {
    kd = newKd;
}

/*
    Return the current Kp value.
*/
float PIDController::getKp() {
    return kp;
}

/*
    Return the current Ki value.
*/
float PIDController::getKi() {
    return ki;
}

/*
    Return the current Kd value.
*/
float PIDController::getKd() {
    return kd;
}