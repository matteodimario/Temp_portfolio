-- View_User_Information
CREATE VIEW View_User_Information AS
SELECT
        users.user_id AS user_id,
        users.first_name AS first_name,
        users.last_name AS last_name,
        users.year_of_birth AS year_of_birth,
        users.month_of_birth AS month_of_birth,
        users.day_of_birth AS day_of_birth,
        users.gender AS gender,
        curr_city_name AS current_city,
        curr_state_name AS current_state,
        curr_country_name AS current_country,
        home_city_name AS hometown_city,
        home_state_name AS hometown_state,
        home_country_name AS hometown_country,
        institution AS institution_name,
        program_year AS program_year,
        concentration AS program_concentration,
        degree AS program_degree
FROM Users users
LEFT JOIN 
(   SELECT curr_cities.user_id, 
           city_name AS curr_city_name, 
           state_name AS curr_state_name,
           country_name AS curr_country_name,
           city_id
    FROM Cities
    LEFT JOIN
    (SELECT current_city_id, user_id FROM User_Current_Cities) curr_cities
    ON city_id = curr_cities.current_city_id
) curr_city_users
ON curr_city_users.user_id = users.user_id
LEFT JOIN
(   SELECT home_cities.user_id, 
           city_name AS home_city_name, 
           state_name AS home_state_name,
           country_name AS home_country_name,
           city_id 
           FROM Cities
    LEFT JOIN
    (SELECT hometown_city_id, 
            user_id FROM User_Hometown_Cities) home_cities
    ON city_id = home_cities.hometown_city_id
) home_city_users
ON home_city_users.user_id = users.user_id
LEFT JOIN
(   SELECT user_id, 
           education.program_id, 
           program_year,
           programs.institution,
           programs.concentration,
           programs.degree
    FROM Education education
    LEFT JOIN
    (SELECT program_id, institution, concentration, degree FROM Programs) programs
    ON education.program_id = programs.program_id
) education_users
ON education_users.user_id = users.user_id;

-- View_Are_Friends
CREATE VIEW View_Are_Friends AS
SELECT user1_id,
       user2_id
FROM Friends;

-- View_Photo_Information
CREATE VIEW View_Photo_Information AS 
SELECT albums.album_id AS album_id,
       albums.album_owner_id AS album_owner_id,
       albums.cover_photo_id AS cover_photo_id,
       albums.album_name AS album_name,
       albums.album_created_time AS album_created_time,
       albums.album_modified_time AS album_modified_time,
       albums.album_link AS album_link,
       albums.album_visibility AS album_visibility,
       photos.photo_id AS photo_id,
       photos.photo_caption AS photo_caption,
       photos.photo_created_time AS photo_created_time,
       photos.photo_modified_time AS photo_modified_time,
       photos.photo_link AS photo_link
FROM Albums albums
LEFT JOIN
(   SELECT photo_id,
           album_id,
           photo_caption,
           photo_created_time,
           photo_modified_time,
           photo_link
    FROM Photos) photos 
ON photos.album_id = albums.album_id;

-- View_Event_Information
CREATE VIEW View_Event_Information AS 
SELECT event_id,
       event_creator_id,
       event_name,
       event_tagline,
       event_description,
       event_host,
       event_type,
       event_subtype,
       event_address,
       cities.city_name AS event_city,
       cities.state_name AS event_state,
       cities.country_name AS event_country,
       event_start_time,
       event_end_time
FROM User_Events user_events
LEFT JOIN
(   SELECT city_name,
           state_name,
           country_name,
           city_id
    FROM Cities) cities
ON cities.city_id = user_events.event_city_id;

-- View_Tag_Information
CREATE VIEW View_Tag_Information AS
SELECT tag_photo_id AS photo_id,
       tag_subject_id,
       tag_created_time,
       tag_x,
       tag_y
FROM Tags;
