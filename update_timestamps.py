#!/usr/bin/env python3
"""
Script to update existing StudentPerformance records with timestamps.
This simulates when the quizzes were taken based on their ID order.
"""

from datetime import datetime, timedelta

from app import app, db
from app.models import StudentPerformance


def update_timestamps():
    with app.app_context():
        # Get all performances without timestamps, ordered by ID
        performances = (
            StudentPerformance.query.filter_by(timestamp=None)
            .order_by(StudentPerformance.id)
            .all()
        )

        if performances:
            print(f"Found {len(performances)} records without timestamps.")

            # Set timestamps starting from 7 days ago, with 1 hour intervals
            base_time = datetime.utcnow() - timedelta(days=7)

            for i, performance in enumerate(performances):
                # Add hours based on ID to simulate different times
                performance.timestamp = base_time + timedelta(hours=i)
                print(
                    f"Updated record {performance.id} with timestamp: {performance.timestamp}"
                )

            db.session.commit()
            print(f"Successfully updated {len(performances)} records with timestamps.")
        else:
            print("All records already have timestamps.")


if __name__ == "__main__":
    update_timestamps()
