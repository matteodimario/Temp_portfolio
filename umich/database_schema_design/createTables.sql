SET AUTOCOMMIT ON;

-- Users Table
CREATE TABLE Users (
    user_id INTEGER,
    first_name VARCHAR2(100) NOT NULL,
    last_name VARCHAR2(100) NOT NULL,
    year_of_birth INTEGER,
    month_of_birth INTEGER,
    day_of_birth INTEGER,
    gender VARCHAR2(100),
    PRIMARY KEY (user_id)
);

-- Friends Table
CREATE TABLE Friends (
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    PRIMARY KEY(user1_id, user2_id),
    FOREIGN KEY(user1_id) REFERENCES Users(user_id),
    FOREIGN KEY(user2_id) REFERENCES Users(user_id),
    CONSTRAINT check_not_self_friend CHECK (user1_id <> user2_id)
);

CREATE TRIGGER Order_Friend_Pairs
    BEFORE INSERT ON Friends
    FOR EACH ROW
        DECLARE temp INTEGER;
        BEGIN
            IF :NEW.user1_id > :NEW.user2_id THEN
                temp := :NEW.user2_id;
                :NEW.user2_id := :NEW.user1_id;
                :NEW.user1_id := temp;
            END IF;
        END;
/

-- ALTER TABLE Users
-- ADD CONSTRAINT user_foreign_key
-- FOREIGN KEY (user1_id, user2_id) REFERENCES Friends
-- INITIALLY DEFERRED DEFERRABLE;

-- Cities Table
CREATE TABLE Cities (
    city_id INTEGER,
    city_name VARCHAR2(100) NOT NULL,
    state_name VARCHAR2(100) NOT NULL,
    country_name VARCHAR2(100) NOT NULL,
    PRIMARY KEY (city_id),
    CONSTRAINT unique_city_state_country UNIQUE (city_name, state_name, country_name)
);

CREATE SEQUENCE City_id_seq
    START WITH 1
    INCREMENT BY 1;
CREATE TRIGGER City_id_trig
    BEFORE INSERT ON Cities
    FOR EACH ROW
        BEGIN
            SELECT city_id_seq.NEXTVAL INTO :NEW.city_id FROM DUAL;
        END;
/

-- User_Current_Cities Table
CREATE TABLE User_Current_Cities (
    user_id INTEGER NOT NULL,
    current_city_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, current_city_id),
    FOREIGN KEY (user_id) REFERENCES Users,
    FOREIGN KEY (current_city_id) REFERENCES Cities(city_id),
    UNIQUE (user_id)
);

-- User_Hometown_Cities Table
CREATE TABLE User_Hometown_Cities (
    user_id INTEGER NOT NULL,
    hometown_city_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, hometown_city_id),
    FOREIGN KEY (user_id) REFERENCES Users,
    FOREIGN KEY (hometown_city_id) REFERENCES Cities(city_id),
    UNIQUE (user_id)
);

-- Messages Table
CREATE TABLE Messages (
    message_id INTEGER,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    message_content VARCHAR2(2000) NOT NULL,
    sent_time TIMESTAMP NOT NULL,
    PRIMARY KEY (message_id),
    FOREIGN KEY (sender_id) REFERENCES Users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES Users(user_id),
    UNIQUE (sender_id, receiver_id)
);

-- Programs Table
CREATE TABLE Programs (
    program_id INTEGER,
    institution VARCHAR2(100) NOT NULL,
    concentration VARCHAR2(200) NOT NULL,
    degree VARCHAR2(100) NOT NULL,
    PRIMARY KEY (program_id),
    UNIQUE(institution, concentration, degree)
    -- Add 'a user cannot list the same program 
    -- multiple times with different graduation years.'
);

CREATE SEQUENCE Program_id_seq
    START WITH 1
    INCREMENT BY 1;
CREATE TRIGGER Program_id_trig
    BEFORE INSERT ON Programs
    FOR EACH ROW
        BEGIN
            SELECT program_id_seq.NEXTVAL INTO :NEW.program_id FROM DUAL;
        END;
/

-- Education Table
CREATE TABLE Education (
    user_id INTEGER NOT NULL,
    program_id INTEGER NOT NULL,
    program_year INTEGER NOT NULL,
    PRIMARY KEY (user_id, program_id),
    FOREIGN KEY (user_id) REFERENCES Users,
    FOREIGN KEY (program_id) REFERENCES Programs
    -- CONSTRAINT unique_program_year UNIQUE(program_id, program_year)
);

-- User_Events Table
CREATE TABLE User_Events (
    event_id INTEGER,
    event_creator_id INTEGER NOT NULL,
    event_name VARCHAR2(100) NOT NULL,
    event_tagline VARCHAR2(100),
    event_description VARCHAR2(100),
    event_host VARCHAR2(100),
    event_type VARCHAR2(100),
    event_subtype VARCHAR2(100),
    event_address VARCHAR2(2000),
    event_city_id INTEGER NOT NULL,
    event_start_time TIMESTAMP,
    event_end_time TIMESTAMP,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_creator_id) REFERENCES Users(user_id),
    FOREIGN KEY (event_city_id) REFERENCES Cities(city_id)
);

-- Participants Table
CREATE TABLE Participants (
    event_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    confirmation VARCHAR2(100) NOT NULL,
    PRIMARY KEY (event_id, user_id),
    FOREIGN KEY (user_id) REFERENCES Users,
    FOREIGN KEY (event_id) REFERENCES User_Events,
    CONSTRAINT confirmation CHECK (
        confirmation = 'Attending'
        OR confirmation = 'Unsure'
        OR confirmation = 'Declines'
        OR confirmation = 'Not_Replied'
    )
);

-- Albums Table
CREATE TABLE Albums (
    album_id INTEGER NOT NULL, 
    album_owner_id INTEGER NOT NULL,
    album_name VARCHAR2(100) NOT NULL, 
    album_created_time TIMESTAMP NOT NULL, 
    album_modified_time TIMESTAMP,
    album_link VARCHAR2(2000) NOT NULL, 
    album_visibility VARCHAR2(100) NOT NULL, 
    cover_photo_id INTEGER NOT NULL, 
    PRIMARY KEY (album_id),
    FOREIGN KEY (album_owner_id) REFERENCES Users(user_id),
    -- FOREIGN KEY (cover_photo_id) REFERENCES Photos(photo_id),
    CONSTRAINT album_visibility CHECK (
        album_visibility = 'Everyone'
        OR album_visibility = 'Friends'
        OR album_visibility = 'Friends_Of_Friends'
        OR album_visibility = 'Myself')
);

-- Photos Table
CREATE TABLE Photos (
    photo_id INTEGER NOT NULL,
    album_id INTEGER NOT NULL,
    photo_caption VARCHAR2(2000),
    photo_created_time TIMESTAMP NOT NULL,
    photo_modified_time TIMESTAMP,
    photo_link VARCHAR2(2000) NOT NULL,
    PRIMARY KEY (photo_id)
);

ALTER TABLE Albums ADD CONSTRAINT albums_photo_id
FOREIGN KEY (cover_photo_id) REFERENCES Photos(photo_id) 
INITIALLY DEFERRED DEFERRABLE;

ALTER TABLE Photos ADD CONSTRAINT photos_album_id
FOREIGN KEY (album_id) REFERENCES Albums(album_id) 
INITIALLY DEFERRED DEFERRABLE;

-- Tags Table
CREATE TABLE Tags (
    tag_photo_id INTEGER,
    tag_subject_id INTEGER,
    tag_created_time TIMESTAMP NOT NULL,
    tag_x NUMBER NOT NULL,
    tag_y NUMBER NOT NULL,
    PRIMARY KEY (tag_photo_id, tag_subject_id),
    FOREIGN KEY (tag_subject_id) REFERENCES Users(user_id),
    FOREIGN KEY (tag_photo_id) REFERENCES Photos(photo_id)
);


