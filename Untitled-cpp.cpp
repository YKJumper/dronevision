

// ----------------------

void calculate_kinetic()
{
    int prev_deviation_x[3] = {target.prev_positions[0].pos.x - config.rotation_center.x,
                               target.prev_positions[1].pos.x - config.rotation_center.x,
                               target.prev_positions[2].pos.x - config.rotation_center.x};
   
    int prev_deviation_y[3] = {target.prev_positions[0].pos.y - config.rotation_center.y,
                               target.prev_positions[1].pos.y - config.rotation_center.y,
                               target.prev_positions[2].pos.y - config.rotation_center.y};
 
    long dt[2] = {time_diff_milli(&target.prev_positions[1].timestamp, &target.prev_positions[0].timestamp),
                  time_diff_milli(&target.prev_positions[2].timestamp, &target.prev_positions[1].timestamp)};
 
    float acceleration_x[2] = {(float)(prev_deviation_x[0] - prev_deviation_x[1]) / (float)dt[0],
                               (float)(prev_deviation_x[1] - prev_deviation_x[2]) / (float)dt[1]};
    float acceleration_y[2] = {(float)(prev_deviation_y[0] - prev_deviation_y[1]) / (float)dt[0],
                               (float)(prev_deviation_y[1] - prev_deviation_y[2]) / (float)dt[1]};
 
    calc_values.kinetic.velocity.x = (float)(prev_deviation_x[0] - prev_deviation_x[2]) / ((dt[0] + dt[1])/1000.0f);
    calc_values.kinetic.velocity.y = (float)(prev_deviation_y[0] - prev_deviation_y[2]) / ((dt[0] + dt[1])/1000.0f);
   
    calc_values.kinetic.acceleration[0].x = isnan(acceleration_x[0]) ? 0 : acceleration_x[0];
    calc_values.kinetic.acceleration[1].x = isnan(acceleration_x[1]) ? 0 : acceleration_x[1];
    calc_values.kinetic.velocity.x = isnan(calc_values.kinetic.velocity.x) ? 0 : calc_values.kinetic.velocity.x;
 
    calc_values.kinetic.acceleration[0].y = isnan(acceleration_y[0]) ? 0 : acceleration_y[0];
    calc_values.kinetic.acceleration[1].y = isnan(acceleration_y[1]) ? 0 : acceleration_y[1];
    calc_values.kinetic.velocity.y = isnan(calc_values.kinetic.velocity.y) ? 0 : calc_values.kinetic.velocity.y;
}

uint16_t calculate_roll()
{
    static float roll = 0.0f;
    switch (states.rc_state_machine.roll) {
        case RC_STATE_MACHINE_IDLE:
            kalman_init(&rc.kalman_filter_roll);
            if (abs(calc_values.deviation.x) > 1) {
                states.rc_state_machine.roll = RC_STATE_MACHINE_MOVEMENT;
            } else {
                roll = rc2deg(rc.prev_state.roll);
            }
        case RC_STATE_MACHINE_MOVEMENT:
            roll = calc_values.kinetic.acceleration[0].x / 0.07f;
            roll = ((calc_values.kinetic.acceleration[0].x + calc_values.kinetic.acceleration[1].x) / 2.0f) / 0.07f;
            break;
        case RC_STATE_MACHINE_BREAKING:
            if (fabsf(states.attitude.roll - calc_values.desire_pose.roll) < 1) {
                states.rc_state_machine.roll = RC_STATE_MACHINE_DONE;
            }
            break;
        case RC_STATE_MACHINE_DONE:
            if (calc_values.deviation.x > 2) {
                states.rc_state_machine.roll = RC_STATE_MACHINE_IDLE;
            }
            break;
    }
    if (roll > max_throttle_level) {
        roll = max_throttle_level;
    } else if (roll < min_throttle_level) {
        roll = min_throttle_level;
    }
    return noramlize_rc(kalman_filter(&rc.kalman_filter_roll, roll));
    return noramlize_rc(roll);
}
 
static int calculate_throttle()
{
    static float throttle = 0;
    static float throttle_start = 0;
    static float coeff = 0.5f;
    switch (states.rc_state_machine.throttle) {
        case RC_STATE_MACHINE_IDLE:
            kalman_init(&rc.kalman_filter_throttle);
            if (!is_target_in_center()) {
                states.rc_state_machine.throttle = RC_STATE_MACHINE_STARTING;
            }
            break;
        case RC_STATE_MACHINE_STARTING:
            throttle_start = rc2deg(rc.prev_state.throttle);
            states.rc_state_machine.throttle = RC_STATE_MACHINE_MOVEMENT;
        case RC_STATE_MACHINE_MOVEMENT:
            if (calc_values.kinetic.acceleration[0].y != 0) {
                throttle = calc_values.kinetic.acceleration[0].y / 0.03f;
            }
            if (is_target_in_center()) {
                states.rc_state_machine.throttle = RC_STATE_MACHINE_BREAKING;
            }
            break;
        case RC_STATE_MACHINE_BREAKING:
            coeff = 0;
            if (!is_target_in_center()) {
                states.rc_state_machine.throttle = RC_STATE_MACHINE_MOVEMENT;
            }
            break;
    }
    if (throttle > max_throttle_level) {
        throttle = max_throttle_level;
    } else if (throttle < min_throttle_level) {
        throttle = min_throttle_level;
    }
    return noramlize_rc(kalman_filter(&rc.kalman_filter_throttle, throttle));
    return noramlize_rc(throttle);
}