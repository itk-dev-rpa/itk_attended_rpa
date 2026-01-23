
CREATE TABLE [dbo].[robots] (
	[name] [varchar](50) PRIMARY KEY,
	[location_url] [varchar](300) NOT NULL,
	[readme_url] [varchar](300) NOT NULL
);

CREATE TABLE [dbo].[history] (
	[time] [datetime] DEFAULT CURRENT_TIMESTAMP,
	[robot_name] [varchar](50) NOT NULL,
	[username] [varchar](50) NOT NULL,
	[machine] [varchar](50) NOT NULL
);

CREATE TABLE [dbo].[constants] (
	[name] [varchar](50) PRIMARY KEY,
	[value] [varchar](300) NOT NULL,
);