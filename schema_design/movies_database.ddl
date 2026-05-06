CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid,
    film_work_id uuid,
    created timestamp with time zone,
    FOREIGN KEY (film_work_id) REFERENCES content.film_work(id),
    FOREIGN KEY (genre_id) REFERENCES content.genre(id)
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid,
    film_work_id uuid,
    role TEXT,
    created timestamp with time zone,
    FOREIGN KEY (person_id) REFERENCES content.person(id),
    FOREIGN KEY (film_work_id) REFERENCES content.film_work(id)
);

CREATE UNIQUE INDEX genre_name_unique ON content.genre (name);
CREATE UNIQUE INDEX genre_film_work_ids_unique 
    ON content.genre_film_work (genre_id, film_work_id);
CREATE UNIQUE INDEX person_film_work_ids_role_unique 
    ON content.person_film_work (person_id, film_work_id, role);
CREATE INDEX genre_film_work_film_work_id_idx ON content.genre_film_work (film_work_id);
CREATE INDEX genre_film_work_genre_id_idx     ON content.genre_film_work (genre_id);
CREATE INDEX person_film_work_film_work_id_idx ON content.person_film_work (film_work_id);
CREATE INDEX person_film_work_person_id_idx    ON content.person_film_work (person_id);
CREATE INDEX film_work_title_idx ON content.film_work (title);
CREATE INDEX film_work_type_idx ON content.film_work (type);
CREATE INDEX film_work_rating_idx ON content.film_work (rating DESC NULLS LAST);
CREATE INDEX film_work_creation_date_idx ON content.film_work (creation_date);
CREATE INDEX film_work_type_rating_idx ON content.film_work (type, rating DESC NULLS LAST);