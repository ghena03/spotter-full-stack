from django.test import SimpleTestCase

from .hos_engine import (
    EVENT_BREAK,
    EVENT_DRIVING,
    EVENT_DROPOFF,
    EVENT_FUEL,
    EVENT_OFF_DUTY,
    EVENT_PICKUP,
    EVENT_RESTART,
    build_trip_schedule,
    calculate_fuel_stops,
    create_event,
    is_break_required,
    limit_driving_hours,
    limit_duty_window_hours,
    plan_trip,
    remaining_cycle_hours,
    remaining_duty_driving_hours,
    remaining_duty_window_hours,
    reset_driving_after_break,
    schedule_driving,
    schedule_driving_with_breaks,
    schedule_duty_period,
    schedule_multi_duty_trip,
)


class HOSPlannerTests(SimpleTestCase):

    # ---------------------------------------------------------
    # Basic HOS limits
    # ---------------------------------------------------------

    def test_driving_under_limit(self):
        result = limit_driving_hours(8)
        self.assertEqual(result, 8)

    def test_driving_at_limit(self):
        result = limit_driving_hours(11)
        self.assertEqual(result, 11)

    def test_driving_over_limit(self):
        result = limit_driving_hours(15)
        self.assertEqual(result, 11)

    def test_negative_driving_is_invalid(self):
        with self.assertRaises(ValueError):
            limit_driving_hours(-1)

    def test_duty_window_under_limit(self):
        result = limit_duty_window_hours(10)
        self.assertEqual(result, 10)

    def test_duty_window_at_limit(self):
        result = limit_duty_window_hours(14)
        self.assertEqual(result, 14)

    def test_duty_window_over_limit(self):
        result = limit_duty_window_hours(18)
        self.assertEqual(result, 14)

    def test_negative_duty_window_is_invalid(self):
        with self.assertRaises(ValueError):
            limit_duty_window_hours(-1)

    # ---------------------------------------------------------
    # 30-minute break rules
    # ---------------------------------------------------------

    def test_break_not_required_before_8_hours(self):
        self.assertFalse(is_break_required(7.5))

    def test_break_required_at_8_hours(self):
        self.assertTrue(is_break_required(8))

    def test_break_required_after_8_hours(self):
        self.assertTrue(is_break_required(9))

    def test_30_minute_break_resets_driving_counter(self):
        result = reset_driving_after_break(
            cumulative_driving_hours=8,
            break_duration_hours=0.5,
        )

        self.assertEqual(result, 0)

    def test_short_break_does_not_reset_driving_counter(self):
        result = reset_driving_after_break(
            cumulative_driving_hours=8,
            break_duration_hours=0.25,
        )

        self.assertEqual(result, 8)

    def test_negative_cumulative_driving_is_invalid(self):
        with self.assertRaises(ValueError):
            is_break_required(-1)

    # ---------------------------------------------------------
    # Event creation
    # ---------------------------------------------------------

    def test_create_driving_event(self):
        event = create_event(
            EVENT_DRIVING,
            start_hour=6,
            end_hour=10,
        )

        self.assertEqual(event["type"], EVENT_DRIVING)
        self.assertEqual(event["start"], 6)
        self.assertEqual(event["end"], 10)
        self.assertEqual(event["duration"], 4)

    def test_event_cannot_have_negative_start(self):
        with self.assertRaises(ValueError):
            create_event(
                EVENT_DRIVING,
                start_hour=-1,
                end_hour=5,
            )

    def test_event_end_must_be_after_start(self):
        with self.assertRaises(ValueError):
            create_event(
                EVENT_DRIVING,
                start_hour=10,
                end_hour=5,
            )

    # ---------------------------------------------------------
    # Simple driving scheduler
    # ---------------------------------------------------------

    def test_schedule_short_trip(self):
        events = schedule_driving(8)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], EVENT_DRIVING)
        self.assertEqual(events[0]["duration"], 8)

    def test_schedule_long_trip(self):
        events = schedule_driving(15)

        self.assertEqual(len(events), 3)

        self.assertEqual(events[0]["type"], EVENT_DRIVING)
        self.assertEqual(events[0]["duration"], 11)

        self.assertEqual(events[1]["type"], EVENT_OFF_DUTY)
        self.assertEqual(events[1]["duration"], 10)

        self.assertEqual(events[2]["type"], EVENT_DRIVING)
        self.assertEqual(events[2]["duration"], 4)

    # ---------------------------------------------------------
    # Duty window
    # ---------------------------------------------------------

    def test_full_duty_window_remaining(self):
        result = remaining_duty_window_hours(0)
        self.assertEqual(result, 14)

    def test_partial_duty_window_remaining(self):
        result = remaining_duty_window_hours(5)
        self.assertEqual(result, 9)

    def test_one_hour_remaining(self):
        result = remaining_duty_window_hours(13)
        self.assertEqual(result, 1)

    def test_duty_window_expired(self):
        result = remaining_duty_window_hours(14)
        self.assertEqual(result, 0)

    def test_duty_window_cannot_be_negative(self):
        result = remaining_duty_window_hours(20)
        self.assertEqual(result, 0)

    def test_negative_elapsed_duty_is_invalid(self):
        with self.assertRaises(ValueError):
            remaining_duty_window_hours(-1)

    # ---------------------------------------------------------
    # 70-hour / 8-day cycle
    # ---------------------------------------------------------

    def test_remaining_cycle_hours_at_start(self):
        self.assertEqual(
            remaining_cycle_hours(0),
            70.0,
        )

    def test_remaining_cycle_hours_partial(self):
        self.assertEqual(
            remaining_cycle_hours(25),
            45.0,
        )

    def test_remaining_cycle_hours_at_limit(self):
        self.assertEqual(
            remaining_cycle_hours(70),
            0.0,
        )

    def test_remaining_cycle_hours_over_limit(self):
        self.assertEqual(
            remaining_cycle_hours(80),
            0.0,
        )

    def test_remaining_cycle_hours_negative(self):
        with self.assertRaises(ValueError):
            remaining_cycle_hours(-1)

    # ---------------------------------------------------------
    # Basic trip planning
    # ---------------------------------------------------------

    def test_plan_trip_uses_cycle_limit(self):
        result = plan_trip(8, 40)

        self.assertEqual(
            result["cycle_remaining_hours"],
            30.0,
        )

        self.assertEqual(
            result["allowed_driving_hours"],
            8.0,
        )

    def test_plan_trip_respects_11_hour_limit(self):
        result = plan_trip(15, 0)

        self.assertEqual(
            result["allowed_driving_hours"],
            11.0,
        )

    def test_plan_trip_respects_cycle_limit(self):
        result = plan_trip(10, 65)

        self.assertEqual(
            result["cycle_remaining_hours"],
            5.0,
        )

        self.assertEqual(
            result["allowed_driving_hours"],
            5.0,
        )

    def test_plan_trip_negative_driving(self):
        with self.assertRaises(ValueError):
            plan_trip(-1, 20)

    # ---------------------------------------------------------
    # Driving with 30-minute breaks
    # ---------------------------------------------------------

    def test_schedule_driving_with_breaks_under_8_hours(self):
        events = schedule_driving_with_breaks(6)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], EVENT_DRIVING)
        self.assertEqual(events[0]["duration"], 6.0)

    def test_schedule_driving_with_breaks_at_8_hours(self):
        events = schedule_driving_with_breaks(8)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["type"], EVENT_DRIVING)
        self.assertEqual(events[0]["duration"], 8.0)

    def test_schedule_driving_with_breaks_over_8_hours(self):
        events = schedule_driving_with_breaks(10)

        self.assertEqual(len(events), 3)

        self.assertEqual(
            events[0]["type"],
            EVENT_DRIVING,
        )
        self.assertEqual(
            events[0]["duration"],
            8.0,
        )

        self.assertEqual(
            events[1]["type"],
            EVENT_BREAK,
        )
        self.assertEqual(
            events[1]["duration"],
            0.5,
        )

        self.assertEqual(
            events[2]["type"],
            EVENT_DRIVING,
        )
        self.assertEqual(
            events[2]["duration"],
            2.0,
        )

    def test_schedule_driving_with_breaks_negative(self):
        with self.assertRaises(ValueError):
            schedule_driving_with_breaks(-1)

    # ---------------------------------------------------------
    # Remaining driving hours
    # ---------------------------------------------------------

    def test_remaining_duty_driving_hours_at_start(self):
        self.assertEqual(
            remaining_duty_driving_hours(0, 0),
            11.0,
        )

    def test_remaining_duty_driving_hours_limited_by_driving(self):
        self.assertEqual(
            remaining_duty_driving_hours(5, 8),
            3.0,
        )

    def test_remaining_duty_driving_hours_limited_by_window(self):
        self.assertEqual(
            remaining_duty_driving_hours(13, 2),
            1.0,
        )

    def test_remaining_duty_driving_hours_window_exhausted(self):
        self.assertEqual(
            remaining_duty_driving_hours(14, 5),
            0.0,
        )

    def test_remaining_duty_driving_hours_negative_window(self):
        with self.assertRaises(ValueError):
            remaining_duty_driving_hours(-1, 0)

    def test_remaining_duty_driving_hours_negative_driving(self):
        with self.assertRaises(ValueError):
            remaining_duty_driving_hours(5, -1)

    # ---------------------------------------------------------
    # Single duty period
    # ---------------------------------------------------------

    def test_schedule_duty_period_short_trip(self):
        result = schedule_duty_period(6)

        self.assertEqual(
            result["driving_hours"],
            6.0,
        )

        self.assertEqual(
            result["remaining_driving_hours"],
            0.0,
        )

        self.assertEqual(
            result["elapsed_duty_hours"],
            6.0,
        )

        self.assertEqual(
            len(result["events"]),
            1,
        )

    def test_schedule_duty_period_adds_break(self):
        result = schedule_duty_period(10)

        self.assertEqual(
            result["driving_hours"],
            10.0,
        )

        self.assertEqual(
            result["remaining_driving_hours"],
            0.0,
        )

        self.assertEqual(
            len(result["events"]),
            3,
        )

        self.assertEqual(
            result["events"][0]["type"],
            EVENT_DRIVING,
        )

        self.assertEqual(
            result["events"][1]["type"],
            EVENT_BREAK,
        )

        self.assertEqual(
            result["events"][2]["type"],
            EVENT_DRIVING,
        )

    def test_schedule_duty_period_respects_11_hour_limit(self):
        result = schedule_duty_period(12)

        self.assertEqual(
            result["driving_hours"],
            11.0,
        )

        self.assertEqual(
            result["remaining_driving_hours"],
            1.0,
        )

    def test_schedule_duty_period_respects_14_hour_window(self):
        result = schedule_duty_period(20)

        self.assertEqual(
            result["driving_hours"],
            11.0,
        )

        self.assertEqual(
            result["remaining_driving_hours"],
            9.0,
        )

    def test_schedule_duty_period_negative(self):
        with self.assertRaises(ValueError):
            schedule_duty_period(-1)

    # ---------------------------------------------------------
    # Multiple duty periods
    # ---------------------------------------------------------

    def test_schedule_multi_duty_trip_short(self):
        events = schedule_multi_duty_trip(6)

        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0]["type"],
            EVENT_DRIVING,
        )
        self.assertEqual(
            events[0]["duration"],
            6.0,
        )

    def test_schedule_multi_duty_trip_requires_reset(self):
        events = schedule_multi_duty_trip(15)

        self.assertEqual(len(events), 5)

        self.assertEqual(
            events[0]["type"],
            EVENT_DRIVING,
        )
        self.assertEqual(
            events[0]["duration"],
            8.0,
        )

        self.assertEqual(
            events[1]["type"],
            EVENT_BREAK,
        )
        self.assertEqual(
            events[1]["duration"],
            0.5,
        )

        self.assertEqual(
            events[2]["type"],
            EVENT_DRIVING,
        )
        self.assertEqual(
            events[2]["duration"],
            3.0,
        )

        self.assertEqual(
            events[3]["type"],
            EVENT_OFF_DUTY,
        )
        self.assertEqual(
            events[3]["duration"],
            10.0,
        )

        self.assertEqual(
            events[4]["type"],
            EVENT_DRIVING,
        )
        self.assertEqual(
            events[4]["duration"],
            4.0,
        )

    def test_schedule_multi_duty_trip_negative(self):
        with self.assertRaises(ValueError):
            schedule_multi_duty_trip(-1)

    # ---------------------------------------------------------
    # Fuel stops
    # ---------------------------------------------------------

    def test_calculate_fuel_stops_short_trip(self):
        stops = calculate_fuel_stops(500)

        self.assertEqual(stops, [])

    def test_calculate_fuel_stops_at_1000_miles(self):
        stops = calculate_fuel_stops(1000)

        self.assertEqual(len(stops), 1)
        self.assertEqual(stops[0], 1000)

    def test_calculate_fuel_stops_long_trip(self):
        stops = calculate_fuel_stops(2500)

        self.assertEqual(
            stops,
            [1000, 2000],
        )

    def test_calculate_fuel_stops_negative_distance(self):
        with self.assertRaises(ValueError):
            calculate_fuel_stops(-100)

    # ---------------------------------------------------------
    # Complete trip schedule
    # ---------------------------------------------------------

    def test_build_trip_schedule_short_trip(self):
        result = build_trip_schedule(
            distance_miles=400,
            driving_hours=6,
            cycle_used_hours=10,
        )

        self.assertIn("events", result)
        self.assertIn("distance_miles", result)
        self.assertIn("driving_hours", result)
        self.assertIn("remaining_driving_hours", result)
        self.assertIn("cycle_remaining_hours", result)
        self.assertIn("total_duration_hours", result)
        self.assertIn("fuel_stops", result)
        self.assertIn("rest_stops", result)
        self.assertIn("breaks", result)
        self.assertIn("cycle_restarts", result)
        self.assertIn("status", result)
        self.assertIn("warnings", result)

        self.assertEqual(
            result["distance_miles"],
            400,
        )

        self.assertEqual(
            result["driving_hours"],
            6,
        )

    def test_build_trip_schedule_includes_pickup_and_dropoff(self):
        result = build_trip_schedule(
            distance_miles=400,
            driving_hours=6,
            cycle_used_hours=10,
        )

        event_types = [
            event["type"]
            for event in result["events"]
        ]

        self.assertIn(
            EVENT_PICKUP,
            event_types,
        )

        self.assertIn(
            EVENT_DROPOFF,
            event_types,
        )

    def test_build_trip_schedule_pickup_and_dropoff_are_one_hour(self):
        result = build_trip_schedule(
            distance_miles=400,
            driving_hours=6,
            cycle_used_hours=10,
        )

        pickup_events = [
            event
            for event in result["events"]
            if event["type"] == EVENT_PICKUP
        ]

        dropoff_events = [
            event
            for event in result["events"]
            if event["type"] == EVENT_DROPOFF
        ]

        self.assertEqual(len(pickup_events), 1)
        self.assertEqual(len(dropoff_events), 1)

        self.assertEqual(
            pickup_events[0]["duration"],
            1.0,
        )

        self.assertEqual(
            dropoff_events[0]["duration"],
            1.0,
        )

    def test_build_trip_schedule_long_trip_has_fuel_stop(self):
        result = build_trip_schedule(
            distance_miles=1800,
            driving_hours=27,
            cycle_used_hours=10,
        )

        event_types = [
            event["type"]
            for event in result["events"]
        ]

        self.assertIn(
            EVENT_FUEL,
            event_types,
        )

        self.assertGreaterEqual(
            len(result["fuel_stops"]),
            1,
        )

    def test_build_trip_schedule_long_trip_has_rest(self):
        result = build_trip_schedule(
            distance_miles=1000,
            driving_hours=15,
            cycle_used_hours=0,
        )

        event_types = [
            event["type"]
            for event in result["events"]
        ]

        self.assertIn(
            EVENT_OFF_DUTY,
            event_types,
        )

        self.assertTrue(
            any(
                event["type"] == EVENT_OFF_DUTY
                and event["duration"] >= 10
                for event in result["events"]
            )
        )

    # ---------------------------------------------------------
    # Cycle restart
    # ---------------------------------------------------------

    def test_build_trip_schedule_adds_restart_when_cycle_is_insufficient(self):
        result = build_trip_schedule(
            distance_miles=100,
            driving_hours=2,
            cycle_used_hours=69.5,
        )

        event_types = [
            event["type"]
            for event in result["events"]
        ]

        self.assertIn(
            EVENT_RESTART,
            event_types,
        )

        self.assertGreaterEqual(
            len(result["cycle_restarts"]),
            1,
        )

    def test_restart_duration_is_34_hours(self):
        result = build_trip_schedule(
            distance_miles=100,
            driving_hours=2,
            cycle_used_hours=69.5,
        )

        restart_events = [
            event
            for event in result["events"]
            if event["type"] == EVENT_RESTART
        ]

        self.assertTrue(
            len(restart_events) >= 1
        )

        self.assertEqual(
            restart_events[0]["duration"],
            34.0,
        )

    # ---------------------------------------------------------
    # HOS safety checks
    # ---------------------------------------------------------

    def test_no_driving_event_exceeds_11_hours(self):
        result = build_trip_schedule(
            distance_miles=1500,
            driving_hours=24,
            cycle_used_hours=0,
        )

        for event in result["events"]:
            if event["type"] == EVENT_DRIVING:
                self.assertLessEqual(
                    event["duration"],
                    11.0,
                )

    def test_break_is_inserted_after_8_hours_of_driving(self):
        result = build_trip_schedule(
            distance_miles=1000,
            driving_hours=12,
            cycle_used_hours=0,
        )

        driving_since_break = 0.0

        for event in result["events"]:
            if event["type"] == EVENT_DRIVING:
                driving_since_break += event["duration"]

                self.assertLessEqual(
                    driving_since_break,
                    8.0,
                )

            elif event["type"] in {
                EVENT_BREAK,
                EVENT_FUEL,
                EVENT_OFF_DUTY,
                EVENT_RESTART,
            }:
                if (
                    event["type"] == EVENT_BREAK
                    and event["duration"] >= 0.5
                ):
                    driving_since_break = 0.0

                elif event["type"] in {
                    EVENT_OFF_DUTY,
                    EVENT_RESTART,
                }:
                    driving_since_break = 0.0

                elif event["type"] == EVENT_FUEL:
                    driving_since_break = 0.0

    def test_long_trip_resets_duty_window_after_10_hours_off_duty(self):
        result = build_trip_schedule(
            distance_miles=1000,
            driving_hours=15,
            cycle_used_hours=0,
        )

        events = result["events"]

        duty_start = 0.0

        for event in events:
            if (
                event["type"] == EVENT_OFF_DUTY
                and event["duration"] >= 10.0
            ):
                duty_start = event["end"]
                continue

            if event["type"] == EVENT_RESTART:
                duty_start = event["end"]
                continue

            if event["type"] == EVENT_DRIVING:
                elapsed_duty = event["end"] - duty_start

                self.assertLessEqual(
                    elapsed_duty,
                    14.0,
                    "Driving continued beyond the 14-hour duty window",
                )

    # ---------------------------------------------------------
    # Result structure
    # ---------------------------------------------------------

    def test_build_trip_schedule_returns_expected_status(self):
        result = build_trip_schedule(
            distance_miles=400,
            driving_hours=6,
            cycle_used_hours=10,
        )

        self.assertIn(
            result["status"],
            {
                "PLANNED",
                "COMPLETED",
                "BLOCKED",
            },
        )

    def test_build_trip_schedule_events_are_chronological(self):
        result = build_trip_schedule(
            distance_miles=1500,
            driving_hours=20,
            cycle_used_hours=10,
        )

        events = result["events"]

        previous_end = 0.0

        for event in events:
            self.assertGreaterEqual(
                event["start"],
                previous_end,
            )

            self.assertGreater(
                event["end"],
                event["start"],
            )

            previous_end = event["end"]

    def test_build_trip_schedule_event_durations_are_positive(self):
        result = build_trip_schedule(
            distance_miles=1500,
            driving_hours=20,
            cycle_used_hours=10,
        )

        for event in result["events"]:
            self.assertGreater(
                event["duration"],
                0,
            )

    # ---------------------------------------------------------
    # Cycle accounting
    # ---------------------------------------------------------

    def test_cycle_hours_are_consumed_by_trip(self):
        result = build_trip_schedule(
            distance_miles=400,
            driving_hours=6,
            cycle_used_hours=10,
        )

        self.assertLess(
            result["cycle_remaining_hours"],
            60.0,
        )

    def test_cycle_remaining_hours_never_negative(self):
        result = build_trip_schedule(
            distance_miles=2000,
            driving_hours=30,
            cycle_used_hours=60,
        )

        self.assertGreaterEqual(
            result["cycle_remaining_hours"],
            0.0,
        )

    # ---------------------------------------------------------
    # Fuel events
    # ---------------------------------------------------------

    def test_fuel_event_has_expected_duration(self):
        result = build_trip_schedule(
            distance_miles=1200,
            driving_hours=18,
            cycle_used_hours=0,
        )

        fuel_events = [
            event
            for event in result["events"]
            if event["type"] == EVENT_FUEL
        ]

        self.assertGreaterEqual(
            len(fuel_events),
            1,
        )

        for event in fuel_events:
            self.assertEqual(
                event["duration"],
                0.5,
            )

    # ---------------------------------------------------------
    # ELD-related event compatibility
    # ---------------------------------------------------------

    def test_events_contain_supported_eld_types(self):
        result = build_trip_schedule(
            distance_miles=1200,
            driving_hours=18,
            cycle_used_hours=0,
        )

        allowed_types = {
            EVENT_DRIVING,
            EVENT_BREAK,
            EVENT_OFF_DUTY,
            EVENT_PICKUP,
            EVENT_DROPOFF,
            EVENT_FUEL,
            EVENT_RESTART,
        }

        for event in result["events"]:
            self.assertIn(
                event["type"],
                allowed_types,
            )