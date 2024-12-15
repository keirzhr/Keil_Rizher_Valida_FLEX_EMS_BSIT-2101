-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 13, 2024 at 03:23 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `flex_ems`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendees`
--

CREATE TABLE `attendees` (
  `attendee_id` int(11) NOT NULL,
  `event_id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `attendee_phone` varchar(11) DEFAULT NULL,
  `attendee_address` varchar(255) DEFAULT NULL,
  `ticket_id` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendees`
--

INSERT INTO `attendees` (`attendee_id`, `event_id`, `name`, `email`, `attendee_phone`, `attendee_address`, `ticket_id`) VALUES
(1, 1, 'Keil Rizher R. Valida', 'keilrizher@mail.com', '09123456712', 'Batangas City', 'T-440450'),
(2, 1, 'Colet', 'colet@mail.com', '09123456783', 'Asgard', 'T-762279'),
(3, 1, 'Gwen', 'gwen@mail.com', '09123456713', 'Wakanda', 'T-137731'),
(4, 4, 'Aiah', 'aiah@mail.com', '09123456714', 'Hogwarts', 'T-459680'),
(5, 6, 'Sheena', 'sheena@mail.com', '09123456715', 'Gotham City', 'T-506718'),
(6, 3, 'Stacey', 'stacey@mail.com', '09123456716', 'Neverland', 'T-364878'),
(7, 5, 'Maloi', 'maloi@mail.com', '09123456717', 'Metropolis', 'T-997403'),
(8, 2, 'Jhoanna', 'jhoanna@mail.com', '09123456718', 'Emerald City', 'T-893569'),
(9, 9, 'Mikha', 'mikha@mail.com', '09123456124', 'Jurassic Park', 'T-747423'),
(10, 9, 'Taylor Swift', 'taylor@mail.com', '09123123442', 'Utopian City', 'T-572737'),
(11, 1, 'Clark Kent', 'superman@mail.com', '09123456712', 'Metropolis', 'T-440450'),
(12, 1, 'Bruce Wayne', 'batman@mail.com', '09123456783', 'Gotham City', 'T-762279'),
(13, 1, 'Diana Prince', 'wonderwoman@mail.com', '09123456713', 'Themyscira', 'T-137731'),
(14, 4, 'Barry Allen', 'flash@mail.com', '09123456714', 'Central City', 'T-459680'),
(15, 6, 'Hal Jordan', 'greenlantern@mail.com', '09123456715', 'Coast City', 'T-506718'),
(16, 3, 'Arthur Curry', 'aquaman@mail.com', '09123456716', 'Atlantis', 'T-364878'),
(17, 5, 'Victor Stone', 'cyborg@mail.com', '09123456717', 'Detroit', 'T-997403'),
(18, 2, 'John Constantine', 'constantine@mail.com', '09123456718', 'London', 'T-893569'),
(19, 9, 'Shazam', 'shazam@mail.com', '09123456124', 'Fawcett City', 'T-747423'),
(20, 9, 'Zatanna Zatara', 'zatanna@mail.com', '09123123442', 'New York', 'T-572737');

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `event_id` int(11) NOT NULL,
  `event_name` varchar(255) NOT NULL,
  `event_date` date DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `organizer_contact` varchar(11) DEFAULT NULL,
  `event_type` varchar(50) NOT NULL,
  `event_image` varchar(255) DEFAULT NULL,
  `max_seats` int(11) DEFAULT 100
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`event_id`, `event_name`, `event_date`, `location`, `description`, `organizer_contact`, `event_type`, `event_image`, `max_seats`) VALUES
(1, 'Taylor Swift: The Eras Tour', '2025-12-18', 'Asgard Philippines', 'Lorem ipsum dolor', '09971671687', 'Concert', 'eras.jpg', 100),
(2, 'Backstreet Boys: DNA World Tour', '2010-12-24', 'Philippine Arena', 'Lorem Ipsum dolor', '09123456789', 'Concert', 'backstreet.jpg', 100),
(3, 'Sublian Festival', '2025-06-23', 'Batangas City', 'Ala eh!!', '09123456780', 'Festival', 'sublian.jpg', 100),
(4, 'Mastering Programming', '2025-10-01', 'BSU Alangilan', 'Lorem Ipsum Dolor', '09123456781', 'Workshop', 'cics.jpg', 100),
(5, 'Cybersecurity Awareness', '2027-12-25', 'Hogwarts', 'Lorem ipsum dolor', '09123456782', 'Conference', 'cybertech.jpg', 100),
(6, 'Graphica Manil', '2025-06-21', 'Narnia', 'lorem ipsum dolor', '09123456783', 'Seminar', 'graphicamanila.jpg', 100),
(7, 'One Direction: Australian Tour', '2026-04-25', 'Manila', 'lorem ipsum dolor', '09123456785', 'Concert', '1D.jpg', 100),
(8, 'Bruno Mars Concert', '2027-12-01', 'Land of Dawn', 'lorem ipsum dolor', '09123456786', 'Concert', 'bruno.jpg', 100),
(9, 'Grand BiniVerse', '2025-02-16', 'Philippine Arena', 'lorem ipsum dolor', '09123456787', 'Concert', 'bini.png', 100),
(10, 'Ed Sheeran Concert updated', '2028-08-10', 'Canada', 'lorem ipsum dolor', '09123456123', 'Concert', 'edsheeran.jpg', 100);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `profile_pic` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`, `full_name`, `email`, `phone`, `profile_pic`) VALUES
(1, 'keil', '5c61d194d5714c7f', 'Keil Rizher updated', 'keilrizher@mail.com', '09971671686', 'uploads\\daniel.jpg'),
(2, 'spiderman', 'c9344c5f1079f7ce', 'Peter Parker', 'peterparker@mail.com', '09989297987', 'uploads\\spiderman_1.jpg'),
(3, 'batman', '1532e76dbe9d43d0', 'Bruce Wayne', 'bruce@mail.com', '00987655678', 'uploads\\batman_2.jpg'),
(4, 'dwayne', '4cc3f3b3897d1ed8', 'Dwayne Johnson', 'dwayne@mail.com', '09876545671', 'uploads\\dwayne_5.jpg'),
(5, 'admin colet', 'd8e94cad8f38dda5', 'Maria Nicolette Vergara', 'marianicolet@mail.com', '09876789098', 'uploads\\colet.png'),
(6, 'maloi', '3ca65ea3501a136d', 'Mary Loi Yves K. Ricalde', 'maryloi@mail.com', '09234565432', 'uploads\\maloi_1.jpg'),
(7, 'harry', 'df46219531cb5d52', 'Harry Potter', 'harry@mail.com', '09123454321', 'uploads\\harry_1.jpg'),
(8, 'taylor', '8e924025a26c584a', 'Taylor Swift', 'taylor@gmail.com', '09123451234', 'uploads\\taylorswift_1.jpg'),
(9, 'mark', '6201eb4dccc956cc', 'Mark Zuckerberg', 'markzuckerberg@mail.com', '09123455233', 'uploads\\zuckerberg_1.jpg'),
(10, 'ironman', '4f278cdddf52263f', 'Tony Stark', 'tonystark@mail.com', '09123454321', 'uploads\\tonyspank_1.png');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendees`
--
ALTER TABLE `attendees`
  ADD PRIMARY KEY (`attendee_id`),
  ADD KEY `ems_event` (`event_id`);

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD PRIMARY KEY (`event_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendees`
--
ALTER TABLE `attendees`
  MODIFY `attendee_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `events`
--
ALTER TABLE `events`
  MODIFY `event_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendees`
--
ALTER TABLE `attendees`
  ADD CONSTRAINT `ems_event` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
