CREATE TABLE x_power (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    area_x_power NUMERIC(6,2),
    hoko_x_power NUMERIC(6,2),
    yagura_x_power NUMERIC(6,2),
    asari_x_power NUMERIC(6,2)
);
