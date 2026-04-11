CREATE TABLE business (
    business_id VARCHAR(30) PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    postal_code VARCHAR(10),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    stars NUMERIC(2,1),
    review_count INTEGER NOT NULL DEFAULT 0,
    is_open INTEGER NOT NULL,
    numCheckins INTEGER NOT NULL DEFAULT 0,
    reviewrating NUMERIC(3,2) NOT NULL DEFAULT 0.0
);

CREATE TABLE business_category (
    business_id VARCHAR(30) NOT NULL,
    category TEXT NOT NULL,
    PRIMARY KEY (business_id, category),
    FOREIGN KEY (business_id) REFERENCES business(business_id)
);

CREATE TABLE business_hours (
    business_id VARCHAR(30) NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL,
    PRIMARY KEY (business_id, day_of_week),
    FOREIGN KEY (business_id) REFERENCES business(business_id)
);

CREATE TABLE business_attribute (
    business_id VARCHAR(30) NOT NULL,
    attribute_name TEXT NOT NULL,
    attribute_value TEXT,
    PRIMARY KEY (business_id, attribute_name),
    FOREIGN KEY (business_id) REFERENCES business(business_id)
);

CREATE TABLE checkin (
    business_id VARCHAR(30) NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    hour_of_day TIME NOT NULL,
    checkin_count INTEGER NOT NULL,
    PRIMARY KEY (business_id, day_of_week, hour_of_day),
    FOREIGN KEY (business_id) REFERENCES business(business_id)
);

CREATE TABLE yelp_user (
    user_id VARCHAR(30) PRIMARY KEY,
    name TEXT NOT NULL,
    review_count INTEGER NOT NULL DEFAULT 0,
    useful INTEGER NOT NULL DEFAULT 0,
    funny INTEGER NOT NULL DEFAULT 0,
    cool INTEGER NOT NULL DEFAULT 0,
    fans INTEGER NOT NULL DEFAULT 0,
    average_stars NUMERIC(3,2),
    yelping_since DATE,
    compliment_cool INTEGER NOT NULL DEFAULT 0,
    compliment_cute INTEGER NOT NULL DEFAULT 0,
    compliment_funny INTEGER NOT NULL DEFAULT 0,
    compliment_hot INTEGER NOT NULL DEFAULT 0,
    compliment_list INTEGER NOT NULL DEFAULT 0,
    compliment_more INTEGER NOT NULL DEFAULT 0,
    compliment_note INTEGER NOT NULL DEFAULT 0,
    compliment_photos INTEGER NOT NULL DEFAULT 0,
    compliment_plain INTEGER NOT NULL DEFAULT 0,
    compliment_profile INTEGER NOT NULL DEFAULT 0,
    compliment_writer INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE user_elite (
    user_id VARCHAR(30) NOT NULL,
    elite_year VARCHAR(4) NOT NULL,
    PRIMARY KEY (user_id, elite_year),
    FOREIGN KEY (user_id) REFERENCES yelp_user(user_id)
);

CREATE TABLE user_friend (
    user_id VARCHAR(30) NOT NULL,
    friend_id VARCHAR(30) NOT NULL,
    PRIMARY KEY (user_id, friend_id),
    FOREIGN KEY (user_id) REFERENCES yelp_user(user_id)
);

CREATE TABLE review (
    review_id VARCHAR(30) PRIMARY KEY,
    business_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(30) NOT NULL,
    stars NUMERIC(2,1) NOT NULL,
    review_date DATE NOT NULL,
    review_text TEXT,
    useful INTEGER NOT NULL DEFAULT 0,
    funny INTEGER NOT NULL DEFAULT 0,
    cool INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (business_id) REFERENCES business(business_id),
    FOREIGN KEY (user_id) REFERENCES yelp_user(user_id)
);