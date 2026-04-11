UPDATE business b
SET numCheckins = COALESCE(t.total_checkins, 0)
FROM temp_checkins AS t
WHERE t.business_id = b.business_id

UPDATE business b
SET review_count = COALESCE(t.total_reviews, 0),
    reviewrating = COALESCE(t.avg_rating, 0)
FROM temp_reviews AS t
WHERE t.business_id = b.business_id
