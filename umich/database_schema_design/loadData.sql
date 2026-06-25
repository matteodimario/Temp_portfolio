-- Users Table populating
INSERT INTO Users 
    (SELECT DISTINCT user_id,
                first_name,
                last_name,
                year_of_birth,
                month_of_birth,
                day_of_birth,
                gender
    FROM project1.Public_User_Information);

-- Friends Table populating
INSERT INTO Friends 
    (SELECT DISTINCT user1_id,
                        user2_id
    FROM project1.Public_Are_Friends);

-- Cities Table populating
INSERT INTO Cities (city_name, state_name, country_name) 
    SELECT DISTINCT city_name,
                    state_name,
                    country_name FROM
    (SELECT DISTINCT current_city AS city_name,
                     current_state AS state_name,
                     current_country AS country_name            
    FROM project1.Public_User_Information)
    UNION
    (SELECT DISTINCT hometown_city AS city_name,
                     hometown_state AS state_name,
                     hometown_country AS country_name
    FROM project1.Public_User_Information);

-- User_Current_Cities Table populating
INSERT INTO User_Current_Cities (
    SELECT DISTINCT pui.user_id,
           cities.city_id
    FROM project1.Public_User_Information pui
    JOIN
    (SELECT city_id,
            city_name AS current_city
     FROM Cities) cities
    ON pui.current_city = cities.current_city);

-- User_Hometown_Cities Table populating
INSERT INTO User_Hometown_Cities (
    SELECT DISTINCT pui.user_id,
           cities.city_id
    FROM project1.Public_User_Information pui
    JOIN 
    (SELECT city_id,
            city_name AS current_city
            FROM Cities) cities
    ON pui.hometown_city = cities.current_city);

-- Messages Table populating
-- Nothing to do

-- Programs Table populating
INSERT INTO Programs (institution, concentration, degree)
    SELECT DISTINCT institution_name AS institution, 
           program_concentration AS concentration,
           program_degree AS degree
    FROM project1.Public_User_Information
    WHERE institution_name IS NOT NULL AND
          program_concentration IS NOT NULL AND
          program_degree IS NOT NULL;

-- Education Table populating
INSERT INTO Education (
    SELECT DISTINCT pui.user_id,
           programs.program_id,
           pui.program_year
    FROM project1.Public_User_Information pui
    JOIN 
    (SELECT programs.program_id,
            programs.institution,
            programs.concentration,
            programs.degree 
    FROM Programs) programs
    ON pui.institution_name = programs.institution AND
       pui.program_concentration = programs.concentration AND
       pui.program_degree = programs.degree
    GROUP BY pui.user_id, programs.program_id, pui.program_year
    HAVING COUNT(*) = 1); 

-- User_Events Table populating
INSERT INTO User_Events(
SELECT DISTINCT event_id,
                event_creator_id,
                event_name,
                event_tagline,
                event_description,
                event_host,
                event_type,
                event_subtype,
                event_address,
                city_id,
                event_start_time,
                event_end_time
FROM ((
    SELECT DISTINCT pei.event_id,
           pei.event_creator_id,
           pei.event_name,
           pei.event_tagline,
           pei.event_description,
           pei.event_host,
           pei.event_type,
           pei.event_subtype,
           pei.event_address,
           cities.city_id,
           pei.event_start_time,
           pei.event_end_time
    FROM project1.Public_Event_Information pei
    JOIN 
    (SELECT DISTINCT city_id,
            city_name
    FROM Cities) cities
    ON pei.event_city = cities.city_name) pei_cities
    JOIN 
    (SELECT DISTINCT user_id
    FROM Users) users
    ON users.user_id = pei_cities.event_creator_id));

-- Albums Table Populating
SET AUTOCOMMIT OFF;
INSERT INTO Albums (
    SELECT DISTINCT album_id, album_owner_id, album_name, 
    album_created_time, album_modified_time, album_link,
    album_visibility, cover_photo_id 
    FROM
    (SELECT DISTINCT ppi.album_id,
           pui.user_id AS album_owner_id,
           ppi.owner_id,
           ppi.album_name,
           ppi.album_created_time,
           ppi.album_modified_time,
           ppi.album_link,
           ppi.album_visibility,
           ppi.cover_photo_id
    FROM project1.Public_Photo_Information ppi
    JOIN
    (SELECT DISTINCT user_id FROM project1.Public_User_Information) pui
    ON pui.user_id = ppi.owner_id));

-- Photos Table Populating
INSERT INTO Photos (
    SELECT DISTINCT photo_id, album_id, photo_caption, photo_created_time,
    photo_modified_time, photo_link
    FROM (
    SELECT DISTINCT ppi.photo_id,
                    ppi.album_id,
                    ppi.photo_caption,
                    ppi.photo_created_time,
                    ppi.photo_modified_time,
                    ppi.photo_link
    FROM project1.Public_Photo_Information ppi
    JOIN 
    (SELECT DISTINCT album_id FROM Albums) albums
    ON albums.album_id = ppi.album_id));
COMMIT;
SET AUTOCOMMIT ON;

-- Tags Table Populating
INSERT INTO Tags (  
    SELECT DISTINCT photo_id, tag_subject_id, tag_created_time,
    tag_x_coordinate, tag_y_coordinate FROM 
    (SELECT DISTINCT pti.photo_id,
                    pti.tag_subject_id,
                    pti.tag_created_time,
                    pti.tag_x_coordinate,
                    pti.tag_y_coordinate
    FROM project1.Public_Tag_Information pti
    JOIN 
    (SELECT DISTINCT user_id FROM project1.Public_user_Information) pui
    ON pui.user_id = pti.tag_subject_id));