"""

Hours of Service (HOS) planning engine.



This module contains the business logic for planning:

- Driving

- 11-hour driving limit

- 14-hour duty window

- 30-minute break requirement

- 10-hour off-duty reset

- 70/8 cycle

- 34-hour restart

- Pickup / Dropoff

- Fuel stops

- ELD daily log sheets

"""



# ============================================================

# HOS CONSTANTS

# ============================================================



MAX_DRIVING_HOURS = 11.0

MAX_DUTY_WINDOW_HOURS = 14.0



BREAK_REQUIRED_AFTER_DRIVING_HOURS = 8.0

BREAK_DURATION_HOURS = 0.5



MIN_OFF_DUTY_RESET_HOURS = 10.0

RESTART_DURATION_HOURS = 34.0



MAX_CYCLE_HOURS = 70.0



FUEL_INTERVAL_MILES = 1000.0

FUEL_DURATION_HOURS = 0.5





# ============================================================

# EVENT TYPES

# ============================================================



EVENT_DRIVING = "DRIVING"

EVENT_ON_DUTY = "ON_DUTY"

EVENT_OFF_DUTY = "OFF_DUTY"

EVENT_SLEEPER = "SLEEPER_BERTH"

EVENT_BREAK = "BREAK"

EVENT_FUEL = "FUEL"

EVENT_PICKUP = "PICKUP"

EVENT_DROPOFF = "DROPOFF"

EVENT_RESTART = "RESTART"





# ============================================================

# BASIC HELPERS

# ============================================================



def limit_driving_hours(requested_hours: float) -> float:

    """

    Return the maximum amount of driving allowed

    in one driving period.

    """



    if requested_hours < 0:

        raise ValueError("Driving hours cannot be negative.")



    return min(requested_hours, MAX_DRIVING_HOURS)





def limit_duty_window_hours(elapsed_hours: float) -> float:

    """

    Return the maximum elapsed time allowed

    in a 14-hour duty window.

    """



    if elapsed_hours < 0:

        raise ValueError("Elapsed hours cannot be negative.")



    return min(elapsed_hours, MAX_DUTY_WINDOW_HOURS)





def is_break_required(cumulative_driving_hours: float) -> bool:

    """

    Return True when the driver has reached the

    8-hour cumulative driving threshold.

    """



    if cumulative_driving_hours < 0:

        raise ValueError(

            "Cumulative driving hours cannot be negative."

        )



    return cumulative_driving_hours >= BREAK_REQUIRED_AFTER_DRIVING_HOURS





def reset_driving_after_break(

    cumulative_driving_hours: float,

    break_duration_hours: float,

) -> float:

    """

    Reset the 8-hour break counter after a qualifying

    30-minute break.

    """



    if cumulative_driving_hours < 0:

        raise ValueError(

            "Cumulative driving hours cannot be negative."

        )



    if break_duration_hours < 0:

        raise ValueError(

            "Break duration cannot be negative."

        )



    if break_duration_hours >= BREAK_DURATION_HOURS:

        return 0.0



    return cumulative_driving_hours





def remaining_duty_window_hours(

    elapsed_duty_hours: float,

) -> float:

    """

    Return remaining time in the current 14-hour

    duty window.

    """



    if elapsed_duty_hours < 0:

        raise ValueError(

            "Elapsed duty hours cannot be negative."

        )



    return max(

        0.0,

        MAX_DUTY_WINDOW_HOURS - elapsed_duty_hours,

    )





def remaining_cycle_hours(

    cycle_used_hours: float,

) -> float:

    """

    Return remaining hours in the 70/8 cycle.



    The 70-hour rule represents on-duty time.

    """



    if cycle_used_hours < 0:

        raise ValueError(

            "Cycle used hours cannot be negative."

        )



    return max(

        0.0,

        MAX_CYCLE_HOURS - cycle_used_hours,

    )





def remaining_duty_driving_hours(

    elapsed_duty_hours: float,

    cumulative_driving_hours: float,

) -> float:

    """

    Return the amount of driving that can still be added

    without exceeding:

    - 14-hour duty window

    - 11-hour driving limit

    """



    if elapsed_duty_hours < 0:

        raise ValueError(

            "Elapsed duty hours cannot be negative."

        )



    if cumulative_driving_hours < 0:

        raise ValueError(

            "Cumulative driving hours cannot be negative."

        )



    remaining_window = remaining_duty_window_hours(

        elapsed_duty_hours

    )



    remaining_driving_limit = (

        MAX_DRIVING_HOURS

        - cumulative_driving_hours

    )



    return max(

        0.0,

        min(

            remaining_window,

            remaining_driving_limit,

        ),

    )





# ============================================================

# EVENT CREATION

# ============================================================



def create_event(

    event_type: str,

    start_hour: float,

    end_hour: float,

) -> dict:

    """

    Create a standardized trip event.

    """



    if start_hour < 0:

        raise ValueError(

            "Start hour cannot be negative."

        )



    if end_hour <= start_hour:

        raise ValueError(

            "End hour must be greater than start hour."

        )



    return {

        "type": event_type,

        "start": round(start_hour, 4),

        "end": round(end_hour, 4),

        "duration": round(

            end_hour - start_hour,

            4,

        ),

    }





# ============================================================

# SIMPLE SCHEDULERS

# ============================================================



def schedule_driving(

    driving_hours: float,

) -> list[dict]:

    """

    Basic multi-period driving schedule.



    Each period allows up to 11 driving hours,

    followed by 10 hours off duty.

    """



    if driving_hours < 0:

        raise ValueError(

            "Driving hours cannot be negative."

        )



    events = []

    remaining = float(driving_hours)

    current_hour = 0.0



    while remaining > 0:

        drive_hours = min(

            remaining,

            MAX_DRIVING_HOURS,

        )



        events.append(

            create_event(

                EVENT_DRIVING,

                current_hour,

                current_hour + drive_hours,

            )

        )



        current_hour += drive_hours

        remaining -= drive_hours



        if remaining > 0:

            events.append(

                create_event(

                    EVENT_OFF_DUTY,

                    current_hour,

                    current_hour

                    + MIN_OFF_DUTY_RESET_HOURS,

                )

            )



            current_hour += (

                MIN_OFF_DUTY_RESET_HOURS

            )



    return events





def schedule_driving_with_breaks(

    driving_hours: float,

) -> list[dict]:

    """

    Schedule driving with 30-minute breaks after

    every 8 cumulative driving hours.



    This helper is mainly useful for isolated driving

    calculations. The complete trip planner uses the

    persistent HOS state in build_trip_schedule().

    """



    if driving_hours < 0:

        raise ValueError(

            "Driving hours cannot be negative."

        )



    events = []

    remaining = float(driving_hours)

    current_hour = 0.0

    cumulative_driving = 0.0



    while remaining > 0:

        driving_until_break = (

            BREAK_REQUIRED_AFTER_DRIVING_HOURS

            - cumulative_driving

        )



        drive_hours = min(

            remaining,

            driving_until_break,

            MAX_DRIVING_HOURS - cumulative_driving,

        )



        if drive_hours > 0:

            events.append(

                create_event(

                    EVENT_DRIVING,

                    current_hour,

                    current_hour + drive_hours,

                )

            )



            current_hour += drive_hours

            remaining -= drive_hours

            cumulative_driving += drive_hours



        if (

            remaining > 0

            and is_break_required(cumulative_driving)

        ):

            events.append(

                create_event(

                    EVENT_BREAK,

                    current_hour,

                    current_hour

                    + BREAK_DURATION_HOURS,

                )

            )



            current_hour += BREAK_DURATION_HOURS



            cumulative_driving = (

                reset_driving_after_break(

                    cumulative_driving,

                    BREAK_DURATION_HOURS,

                )

            )



    return events





def schedule_duty_period(

    driving_hours: float,

) -> dict:

    """

    Schedule one duty period while respecting:



    - 11-hour maximum driving

    - 14-hour duty window

    - 30-minute break after 8 cumulative driving hours



    This function does NOT reset the 11-hour driving

    limit when the 30-minute break occurs.

    """



    if driving_hours < 0:

        raise ValueError(

            "Driving hours cannot be negative."

        )



    events = []



    remaining = float(driving_hours)



    elapsed_duty_hours = 0.0

    total_duty_driving_hours = 0.0

    cumulative_driving_since_break = 0.0



    while remaining > 0:

        remaining_window = (

            remaining_duty_window_hours(

                elapsed_duty_hours

            )

        )



        remaining_11_hour_limit = (

            MAX_DRIVING_HOURS

            - total_duty_driving_hours

        )



        available_driving = max(

            0.0,

            min(

                remaining_window,

                remaining_11_hour_limit,

            ),

        )



        if available_driving <= 0:

            break



        driving_until_break = (

            BREAK_REQUIRED_AFTER_DRIVING_HOURS

            - cumulative_driving_since_break

        )



        drive_hours = min(

            remaining,

            available_driving,

            driving_until_break,

        )



        if drive_hours > 0:

            events.append(

                create_event(

                    EVENT_DRIVING,

                    elapsed_duty_hours,

                    elapsed_duty_hours

                    + drive_hours,

                )

            )



            elapsed_duty_hours += drive_hours

            total_duty_driving_hours += drive_hours

            cumulative_driving_since_break += (

                drive_hours

            )

            remaining -= drive_hours



        if (

            remaining > 0

            and is_break_required(

                cumulative_driving_since_break

            )

        ):

            events.append(

                create_event(

                    EVENT_BREAK,

                    elapsed_duty_hours,

                    elapsed_duty_hours

                    + BREAK_DURATION_HOURS,

                )

            )



            elapsed_duty_hours += (

                BREAK_DURATION_HOURS

            )



            cumulative_driving_since_break = (

                reset_driving_after_break(

                    cumulative_driving_since_break,

                    BREAK_DURATION_HOURS,

                )

            )



    return {

        "events": events,

        "driving_hours": total_duty_driving_hours,

        "remaining_driving_hours": remaining,

        "elapsed_duty_hours": elapsed_duty_hours,

    }





def schedule_multi_duty_trip(

    driving_hours: float,

) -> list[dict]:

    """

    Schedule driving across multiple duty periods.

    """



    if driving_hours < 0:

        raise ValueError(

            "Driving hours cannot be negative."

        )



    events = []

    remaining = float(driving_hours)

    current_hour = 0.0



    while remaining > 0:

        duty_result = schedule_duty_period(

            remaining

        )



        for event in duty_result["events"]:

            events.append(

                create_event(

                    event["type"],

                    current_hour + event["start"],

                    current_hour + event["end"],

                )

            )



        current_hour += (

            duty_result["elapsed_duty_hours"]

        )



        remaining = (

            duty_result["remaining_driving_hours"]

        )



        if remaining > 0:

            events.append(

                create_event(

                    EVENT_OFF_DUTY,

                    current_hour,

                    current_hour

                    + MIN_OFF_DUTY_RESET_HOURS,

                )

            )



            current_hour += (

                MIN_OFF_DUTY_RESET_HOURS

            )



    return events





# ============================================================

# BASIC TRIP PLANNER

# ============================================================



def plan_trip(

    driving_hours: float,

    cycle_used_hours: float,

):

    """

    Basic trip planning calculation using remaining

    70/8 cycle hours.

    """



    if driving_hours < 0:

        raise ValueError(

            "Driving hours cannot be negative."

        )



    if cycle_used_hours < 0:

        raise ValueError(

            "Cycle used hours cannot be negative."

        )



    cycle_remaining = remaining_cycle_hours(

        cycle_used_hours

    )



    allowed_driving = min(

        driving_hours,

        MAX_DRIVING_HOURS,

        cycle_remaining,

    )



    return {

        "driving_hours": driving_hours,

        "cycle_used_hours": cycle_used_hours,

        "cycle_remaining_hours": cycle_remaining,

        "allowed_driving_hours": allowed_driving,

        "events": [],

    }





# ============================================================

# FUEL STOPS

# ============================================================



class FuelStopMarker(int):
    """Integer-like fuel marker that also supports legacy dict-style access."""

    def __new__(cls, mile_marker):
        return int.__new__(cls, int(mile_marker))

    def __getitem__(self, key):
        if key == "type":
            return EVENT_FUEL
        if key == "mile_marker":
            return int(self)
        if key == "duration_hours":
            return FUEL_DURATION_HOURS
        raise KeyError(key)




def calculate_fuel_stops(

    distance_miles: float,

):

    """Return fuel-stop mile markers every 1,000 miles."""

    if distance_miles < 0:

        raise ValueError("distance_miles cannot be negative")

    stops = []

    mile_marker = FUEL_INTERVAL_MILES

    while mile_marker <= distance_miles:

        stops.append(FuelStopMarker(mile_marker))

        mile_marker += FUEL_INTERVAL_MILES

    return stops




def _add_event(

    events: list,

    event_type: str,

    current_time: float,

    duration: float,

):

    """

    Append an event and return the new current time.

    """



    if duration <= 0:

        return current_time



    events.append(

        create_event(

            event_type,

            current_time,

            current_time + duration,

        )

    )



    return current_time + duration





def _add_off_duty_reset(

    events: list,

    current_time: float,

):

    """

    Add the required 10-hour off-duty reset.

    """



    new_time = _add_event(

        events,

        EVENT_OFF_DUTY,

        current_time,

        MIN_OFF_DUTY_RESET_HOURS,

    )



    return new_time





def _add_restart(

    events: list,

    current_time: float,

):

    """

    Add a 34-hour restart.



    A 34-hour restart resets:

    - 70/8 cycle

    - 14-hour duty window

    - 11-hour driving period

    - 8-hour break counter

    """



    new_time = _add_event(

        events,

        EVENT_RESTART,

        current_time,

        RESTART_DURATION_HOURS,

    )



    return new_time





# ============================================================

# COMPLETE TRIP SCHEDULER

# ============================================================



def build_trip_schedule(
    distance_miles,
    driving_hours,
    cycle_used_hours=0.0,
    pickup_hours=1.0,
    dropoff_hours=1.0,
    
):

    """
    Build a complete trip schedule.
    HOS rules handled here:
    1. Maximum 11 driving hours per duty period.
    2. Maximum 14 consecutive hours in a duty window.
    3. 30-minute break after 8 cumulative driving hours.
    4. 10 consecutive hours off duty to reset the
       driving/duty period.
    5. 70-hour / 8-day cycle.
    6. Automatic 34-hour restart when the cycle is exhausted.
    7. Pickup and dropoff count as on-duty time.
    8. Fuel stops every 1,000 miles.
    9. A 30-minute fuel stop can reset the 8-hour
       driving-break counter.
    """



    # Validation



    if distance_miles < 0:
        raise ValueError(
            "distance_miles cannot be negative"
        )



    if driving_hours < 0:

        raise ValueError(

            "driving_hours cannot be negative"

        )



    if cycle_used_hours < 0:

        raise ValueError(

            "cycle_used_hours cannot be negative"

        )



    if cycle_used_hours > MAX_CYCLE_HOURS:

        raise ValueError(

            "cycle_used_hours cannot exceed 70"

        )



    if pickup_hours < 0:

        raise ValueError(

            "pickup_hours cannot be negative"

        )



    if dropoff_hours < 0:

        raise ValueError(

            "dropoff_hours cannot be negative"

        )



    if pickup_hours > MAX_DUTY_WINDOW_HOURS:

        raise ValueError(

            "pickup_hours cannot exceed 14 hours"

        )



    if dropoff_hours > MAX_DUTY_WINDOW_HOURS:

        raise ValueError(

            "dropoff_hours cannot exceed 14 hours"

        )



    # --------------------------------------------------------

    # Empty trip

    # --------------------------------------------------------



    if driving_hours == 0:

        return {

            "events": [],

            "distance_miles": float(distance_miles),

            "driving_hours": 0.0,

            "remaining_driving_hours": 0.0,

            "cycle_remaining_hours": remaining_cycle_hours(

                cycle_used_hours

            ),

            "total_duration_hours": 0.0,

            "fuel_stops": [],

            "rest_stops": [],

            "breaks": [],

            "cycle_restarts": [],

            "status": "PLANNED",

            "warnings": [],

        }



    # --------------------------------------------------------

    # Initial state

    # --------------------------------------------------------



    events = []



    current_time = 0.0



    remaining_driving = float(driving_hours)



    distance_travelled = 0.0



    cycle_remaining = remaining_cycle_hours(

        cycle_used_hours

    )



    # Time elapsed since the current 14-hour window began.

    duty_window_elapsed = 0.0



    # Driving hours used inside the current 11-hour

    # driving period.

    driving_in_duty_period = 0.0



    # Driving hours since the last qualifying 30-minute

    # non-driving break.

    driving_since_break = 0.0



    cycle_restarts = []



    warnings = []



    # --------------------------------------------------------

    # Average route speed

    # --------------------------------------------------------



    if distance_miles > 0:

        average_speed = (

            float(distance_miles)

            / float(driving_hours)

        )

    else:

        average_speed = 0.0



    # --------------------------------------------------------

    # Fuel stops

    # --------------------------------------------------------



    fuel_stops = calculate_fuel_stops(

        distance_miles

    )



    fuel_index = 0



    # --------------------------------------------------------

    # Pickup

    # --------------------------------------------------------



    if pickup_hours > 0:



        # If there isn't enough cycle time,

        # restart before starting on-duty work.

        if cycle_remaining < pickup_hours:

            current_time = _add_restart(

                events,

                current_time,

            )



            cycle_remaining = MAX_CYCLE_HOURS

            duty_window_elapsed = 0.0

            driving_in_duty_period = 0.0

            driving_since_break = 0.0



            cycle_restarts.append(

    events[-1]

)



        current_time = _add_event(

            events,

            EVENT_PICKUP,

            current_time,

            pickup_hours,)



        duty_window_elapsed += pickup_hours

        cycle_remaining -= pickup_hours



    # --------------------------------------------------------

    # Main trip loop

    # --------------------------------------------------------



    while remaining_driving > 0.000001:



        # ----------------------------------------------------

        # Cycle exhausted

        # ----------------------------------------------------



        if cycle_remaining <= 0.000001:



            current_time = _add_restart(

                events,

                current_time,

            )



            cycle_remaining = MAX_CYCLE_HOURS

            duty_window_elapsed = 0.0

            driving_in_duty_period = 0.0

            driving_since_break = 0.0



            cycle_restarts.append(events[-1])



            continue



        # ----------------------------------------------------

        # Duty window / 11-hour limit reached

        # ----------------------------------------------------



        if (

            duty_window_elapsed

            >= MAX_DUTY_WINDOW_HOURS - 0.000001

            or driving_in_duty_period

            >= MAX_DRIVING_HOURS - 0.000001

        ):



            current_time = _add_off_duty_reset(

                events,

                current_time,

            )



            duty_window_elapsed = 0.0

            driving_in_duty_period = 0.0

            driving_since_break = 0.0



            continue



        # ----------------------------------------------------

        # 30-minute break required

        # ----------------------------------------------------



        if (

            driving_since_break

            >= BREAK_REQUIRED_AFTER_DRIVING_HOURS

            - 0.000001

        ):



            remaining_window = (

                MAX_DUTY_WINDOW_HOURS

                - duty_window_elapsed

            )



            # If there is not enough room for the

            # 30-minute break inside the 14-hour window,

            # take the 10-hour reset instead.

            if remaining_window < (

                BREAK_DURATION_HOURS - 0.000001

            ):



                current_time = _add_off_duty_reset(

                    events,

                    current_time,

                )



                duty_window_elapsed = 0.0

                driving_in_duty_period = 0.0

                driving_since_break = 0.0



                continue



            current_time = _add_event(

                events,

                EVENT_BREAK,

                current_time,

                BREAK_DURATION_HOURS,

            )



            duty_window_elapsed += (

                BREAK_DURATION_HOURS

            )



            driving_since_break = 0.0



            continue



        # ----------------------------------------------------

        # Find next fuel stop

        # ----------------------------------------------------



        next_fuel_distance = None



        if fuel_index < len(fuel_stops):

            next_fuel_distance = fuel_stops[fuel_index]



        if (

            next_fuel_distance is not None

            and average_speed > 0

        ):



            distance_until_fuel = (

                next_fuel_distance

                - distance_travelled

            )



            driving_until_fuel = (

                distance_until_fuel

                / average_speed

            )



            # Prevent tiny floating point negatives.

            driving_until_fuel = max(

                0.0,

                driving_until_fuel,

            )



        else:

            driving_until_fuel = (

                remaining_driving

            )



        # ----------------------------------------------------

        # Calculate how much we can drive now

        # ----------------------------------------------------



        remaining_window = (

            MAX_DUTY_WINDOW_HOURS

            - duty_window_elapsed

        )



        remaining_11_hour_limit = (

            MAX_DRIVING_HOURS

            - driving_in_duty_period

        )



        remaining_break_limit = (

            BREAK_REQUIRED_AFTER_DRIVING_HOURS

            - driving_since_break

        )



        drive_now = min(

            remaining_driving,

            remaining_window,

            remaining_11_hour_limit,

            remaining_break_limit,

            cycle_remaining,

            driving_until_fuel,

        )



        # ----------------------------------------------------

        # Drive

        # ----------------------------------------------------



        if drive_now > 0.000001:



            events.append(

                create_event(

                    EVENT_DRIVING,

                    current_time,

                    current_time + drive_now,

                )

            )



            current_time += drive_now



            remaining_driving -= drive_now



            duty_window_elapsed += drive_now



            driving_in_duty_period += drive_now



            driving_since_break += drive_now



            cycle_remaining -= drive_now



            distance_travelled += (

                drive_now * average_speed

            )



            # Avoid floating-point errors around

            # exact fuel markers.

            if (

                next_fuel_distance is not None

                and distance_travelled

                >= next_fuel_distance - 0.0001

            ):

                distance_travelled = (

                    next_fuel_distance

                )



        # ----------------------------------------------------

        # Trip completed

        # ----------------------------------------------------



        if remaining_driving <= 0.000001:

            remaining_driving = 0.0

            break



        # ----------------------------------------------------

        # Fuel stop reached

        # ----------------------------------------------------



        if (

            next_fuel_distance is not None

            and distance_travelled

            >= next_fuel_distance - 0.0001

        ):



            # Fuel is on-duty, so it consumes both

            # duty-window time and cycle time.

            if cycle_remaining < (

                FUEL_DURATION_HOURS - 0.000001

            ):



                current_time = _add_restart(

                    events,

                    current_time,

                )



                cycle_remaining = MAX_CYCLE_HOURS

                duty_window_elapsed = 0.0

                driving_in_duty_period = 0.0

                driving_since_break = 0.0



                cycle_restarts.append(events[-1])



                continue



            # Fuel cannot extend beyond the 14-hour

            # duty window. Reset first if necessary.

            if (

                duty_window_elapsed

                + FUEL_DURATION_HOURS

                > MAX_DUTY_WINDOW_HOURS

                + 0.000001

            ):



                current_time = _add_off_duty_reset(

                    events,

                    current_time,

                )



                duty_window_elapsed = 0.0

                driving_in_duty_period = 0.0

                driving_since_break = 0.0



                continue



            current_time = _add_event(

                events,

                EVENT_FUEL,

                current_time,

                FUEL_DURATION_HOURS,

            )



            duty_window_elapsed += (

                FUEL_DURATION_HOURS

            )



            cycle_remaining -= (

                FUEL_DURATION_HOURS

            )



            # A 30-minute non-driving fuel stop can

            # satisfy/reset the 8-hour break counter.

            driving_since_break = 0.0



            fuel_index += 1



            continue



        # ----------------------------------------------------

        # If driving was blocked, loop back so the correct

        # HOS reset/break/restart is applied.

        # ----------------------------------------------------



        if drive_now <= 0.000001:



            # Cycle will be handled at the beginning

            # of the next iteration.

            if cycle_remaining <= 0.000001:

                continue



            # 30-minute break will be handled next.

            if (

                driving_since_break

                >= BREAK_REQUIRED_AFTER_DRIVING_HOURS

                - 0.000001

            ):

                continue



            # 11-hour / 14-hour reset will be handled next.

            if (

                driving_in_duty_period

                >= MAX_DRIVING_HOURS

                - 0.000001

                or duty_window_elapsed

                >= MAX_DUTY_WINDOW_HOURS

                - 0.000001

            ):

                continue



            # Safety guard to prevent an infinite loop

            # in case of unexpected floating-point state.

            warnings.append(

                "Trip scheduling stopped because no legal "

                "driving time was available."

            )

            break



    # --------------------------------------------------------

    # Dropoff

    # --------------------------------------------------------



    if remaining_driving <= 0.000001:



        if dropoff_hours > 0:



            # Dropoff is on-duty and consumes cycle hours.

            if cycle_remaining < dropoff_hours:



                current_time = _add_restart(

                    events,

                    current_time,

                )



                cycle_remaining = MAX_CYCLE_HOURS

                duty_window_elapsed = 0.0

                driving_in_duty_period = 0.0

                driving_since_break = 0.0



                cycle_restarts.append(events[-1])



            # Dropoff cannot extend beyond the 14-hour

            # window.

            if (

                duty_window_elapsed

                + dropoff_hours

                > MAX_DUTY_WINDOW_HOURS

                + 0.000001

            ):



                current_time = _add_off_duty_reset(

                    events,

                    current_time,

                )



                duty_window_elapsed = 0.0

                driving_in_duty_period = 0.0

                driving_since_break = 0.0



            current_time = _add_event(

                events,

                EVENT_DROPOFF,

                current_time,

                dropoff_hours,

            )



            duty_window_elapsed += dropoff_hours

            cycle_remaining -= dropoff_hours



    else:

        warnings.append(

            "Trip could not be completed within the "

            "available HOS constraints."

        )



    # --------------------------------------------------------

    # Derived event lists

    # --------------------------------------------------------



    fuel_events = [

        event

        for event in events

        if event["type"] == EVENT_FUEL

    ]



    break_events = [

        event

        for event in events

        if event["type"] == EVENT_BREAK

    ]



    rest_events = [

        event

        for event in events

        if (

            event["type"] == EVENT_OFF_DUTY

            and event["duration"]

            >= MIN_OFF_DUTY_RESET_HOURS

        )

        or event["type"] == EVENT_RESTART

    ]



    # --------------------------------------------------------

    # Final result

    # --------------------------------------------------------

    # --------------------------------------------------------
# Final result
# --------------------------------------------------------

    status = (
    "PLANNED"
    if remaining_driving <= 0.000001
    else "PARTIAL"
)

    daily_logs = build_eld_daily_logs(events)

    return {

 

        "events": events,
        "daily_logs": daily_logs,
        "distance_miles": float(distance_miles),
        "driving_hours": float(driving_hours),
        "remaining_driving_hours": round(
            max(0.0, remaining_driving),

            4,

        ),

        "cycle_remaining_hours": round(

            max(0.0, cycle_remaining),

            4,

        ),

        "total_duration_hours": round(
            current_time,
            4,
        ),

        "fuel_stops": fuel_events,
        "rest_stops": rest_events,
        "breaks": break_events,
        "cycle_restarts": cycle_restarts,
        "status": status,
        "warnings": warnings,
    }


# COMPATIBILITY WRAPPER




def plan_trip_schedule(
    driving_hours,
    cycle_used_hours=0.0,
    pickup_hours=1.0,
    dropoff_hours=1.0,
):

    """

    Compatibility wrapper for the previous API.
    This function does not know the actual route distance,
    so it delegates to the complete HOS scheduler without
    fuel stops.
    """



    result = build_trip_schedule(

        distance_miles=0.0,

        driving_hours=driving_hours,

        cycle_used_hours=cycle_used_hours,

        pickup_hours=pickup_hours,

        dropoff_hours=dropoff_hours,

    )



    return result





# ============================================================

# ELD DAILY LOGS

# ============================================================



ELD_DAY_HOURS = 24.0



ELD_STATUS_DRIVING = "DRIVING"

ELD_STATUS_ON_DUTY = "ON_DUTY"

ELD_STATUS_OFF_DUTY = "OFF_DUTY"





def event_to_eld_status(event_type):

    """

    Convert trip events into ELD duty statuses.

    """



    if event_type == EVENT_DRIVING:

        return ELD_STATUS_DRIVING



    if event_type in {

        EVENT_PICKUP,

        EVENT_DROPOFF,

        EVENT_FUEL,

        EVENT_ON_DUTY,

    }:

        return ELD_STATUS_ON_DUTY



    if event_type in {

        EVENT_OFF_DUTY,

        EVENT_BREAK,

        EVENT_SLEEPER,

        EVENT_RESTART,

    }:

        return ELD_STATUS_OFF_DUTY



    return ELD_STATUS_ON_DUTY





def build_eld_daily_logs(events):

    """

    Split trip events into 24-hour ELD daily logs.



    Events crossing midnight are split into separate

    daily segments.

    """



    if not events:

        return []



    daily_logs = {}



    for event in events:



        start = float(event["start"])

        end = float(event["end"])



        if end <= start:

            continue



        status = event_to_eld_status(

            event["type"]

        )



        current_time = start



        while current_time < end:



            day_number = (

                int(

                    current_time

                    // ELD_DAY_HOURS

                )

                + 1

            )



            day_start = (

                (day_number - 1)

                * ELD_DAY_HOURS

            )



            day_end = (

                day_number

                * ELD_DAY_HOURS

            )



            segment_start = current_time



            segment_end = min(

                end,

                day_end,

            )



            daily_logs.setdefault(

                day_number,

                [],

            ).append(

                {

                    "status": status,

                    "start": round(

                        segment_start

                        - day_start,

                        4,

                    ),

                    "end": round(

                        segment_end

                        - day_start,

                        4,

                    ),

                    "duration": round(

                        segment_end

                        - segment_start,

                        4,

                    ),

                    "event_type": event[

                        "type"

                    ],

                }

            )



            current_time = segment_end



    return [

        {

            "day": day_number,

            "events": daily_logs[

                day_number

            ],

        }

        for day_number in sorted(

            daily_logs

        )

    ]