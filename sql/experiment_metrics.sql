WITH base AS (
    SELECT
        variant,
        user_id,
        CASE WHEN converted = 1 THEN 1 ELSE 0 END AS converted,
        acquisition_channel,
        device_type,
        region
    FROM experiment_data
)

SELECT
    variant,
    COUNT(DISTINCT user_id) AS users,
    SUM(converted) AS conversions,
    AVG(CAST(converted AS FLOAT)) AS conversion_rate
FROM base
GROUP BY variant
ORDER BY variant;

WITH base AS (
    SELECT
        variant,
        acquisition_channel,
        CASE WHEN converted = 1 THEN 1 ELSE 0 END AS converted
    FROM experiment_data
)
SELECT
    acquisition_channel,
    variant,
    COUNT(*) AS users,
    AVG(CAST(converted AS FLOAT)) AS conversion_rate
FROM base
GROUP BY acquisition_channel, variant
ORDER BY acquisition_channel, variant;

WITH base AS (
    SELECT
        variant,
        device_type,
        CASE WHEN converted = 1 THEN 1 ELSE 0 END AS converted
    FROM experiment_data
)
SELECT
    device_type,
    variant,
    COUNT(*) AS users,
    AVG(CAST(converted AS FLOAT)) AS conversion_rate
FROM base
GROUP BY device_type, variant
ORDER BY device_type, variant;