
-- This script creates dummy data for testing purposes.

INSERT INTO TABLE `user` (username, age) VALUES
('Alice', 30),
('Bob', 25),
('Charlie', 35),
('David', 28),
('Eve', 22);

INSERT INTO bpm_table (userID, bpm, time_stamp) VALUES
(1, 72, '2023-10-01 08:00:00'),
(1, 75, '2023-10-01 09:00:00'),
(2, 80, '2023-10-01 08:30:00'),
(2, 78, '2023-10-01 09:30:00'),
(3, 70, '2023-10-01 08:15:00'),
(4, 85, '2023-10-01 08:45:00'),
(5, 90, '2023-10-01 09:15:00');

INSERT INTO oxygen_level_table (userID, oxygen_level, time_stamp) VALUES
(1, 98, '2023-10-01 08:00:00'),
(1, 97, '2023-10-01 09:00:00'),
(2, 95, '2023-10-01 08:30:00'),
(2, 96, '2023-10-01 09:30:00'),
(3, 99, '2023-10-01 08:15:00'),
(4, 94, '2023-10-01 08:45:00'),
(5, 92, '2023-10-01 09:15:00');

