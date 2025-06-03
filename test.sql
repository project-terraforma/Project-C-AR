-- LOAD spatial; --noqa
-- LOAD httpfs;  -- noqa
-- -- SET azure_storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=overturemapswestus2;AccountKey=;EndpointSuffix=core.windows.net';

-- COPY(
--   SELECT
--     id,
--     names.primary as primary_name,
--     height,
--     geometry   -- DuckDB v.1.1.0 will autoload this as a `geometry` type
--   FROM read_parquet('azure://release/2025-04-23.0/theme=buildings/type=building/*', filename=true, hive_partitioning=1)
--   WHERE names.primary IS NOT NULL and confidence > .95
--   AND bbox.xmin BETWEEN -121.91 AND -121.88
--   AND bbox.ymin BETWEEN 37.40 AND 37.43
--   LIMIT 400
-- ) TO 'greatmall.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');

----------------------------------------------------------------
LOAD spatial; -- noqa

SET s3_region='us-west-2';

COPY(                                       -- COPY <query> TO <output> saves the results to disk.
    SELECT
       id,
       names.primary as name,
       confidence AS confidence,
       CAST(socials AS JSON) as socials,    -- Ensure each attribute can be serialized to JSON
       geometry                             -- DuckDB understands this to be a geometry type
    FROM read_parquet('s3://overturemaps-us-west-2/release/2025-04-23.0/theme=places/type=place/*', filename=true, hive_partitioning=1)
    WHERE categories.primary IS NOT NULL and confidence > 0.95 -- = 'pizza_restaurant'
    AND bbox.xmin BETWEEN -121.91 AND -121.88       -- Only use the bbox min values
    AND bbox.ymin BETWEEN 37.40 AND 37.43         -- because they are point geometries.

) TO 'places.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');

-- LOAD spatial; -- noqa

-- SET s3_region='us-west-2';

-- COPY(                                       -- COPY <query> TO <output> saves the results to disk.
--     SELECT
--        id,
--        names.primary as name,
--        confidence AS confidence,
--        CAST(socials AS JSON) as socials,    -- Ensure each attribute can be serialized to JSON
--        geometry                             -- DuckDB understands this to be a geometry type
--     FROM read_parquet('s3://overturemaps-us-west-2/release/2025-04-23.0/theme=places/type=place/*', filename=true, hive_partitioning=1)
--     WHERE categories.primary IS NOT NULL and confidence > 0.95 -- = 'pizza_restaurant'
--     AND bbox.xmin BETWEEN -122.06 AND -121.98
--     AND bbox.ymin BETWEEN 36.94 AND 36.98


-- ) TO 'places.geojson' WITH (FORMAT GDAL, DRIVER 'GeoJSON');