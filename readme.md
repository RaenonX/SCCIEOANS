# IE Office Appointment Notifying System (IEOANS)
This system is designed to let students know that it is their turn for the appointment. This idea inherited from the existing people calling system in the Cashier.

_All contents are subject to change._

## Contents
[Objective](#Objective)
[Tools](#tools)
[Program Structure](#program-structure)

## Objective
To create a system which can notify people that it is going to be their turn, they should head to the IE office.
### Pending Additional Function
* Let users know their appointment queue position
* Notify users when their appointment date/time is close
* Let users schedule an appointment through this portal
* Let users can directly contact advisors (or just add a button with a mailto protocol hyperlink)
* Let users access some frequently used functions on the school official website, such as class schedule and transcripts, in their language, as these webpages are not mobile friendly

## Tools
### Frontend Language: HTML, CSS, javascript, jQuery, bootstrap3
No exception, all webpages requires HTML. CSS and bootstrap3 will make the looking of the website beautiful; javascript and jQuery can let our webpage be more interactive.
> The reason of using bootstrap 3 is because that Flask-bootstrap are currently only support this version.
### Backend Language: Python 3
The reason of using Python 3 is because:
* This is the language which CS 121 student is using, and it also can implement things which is taught in CS 141 and CS 143.
* PyPI contains a lot of package, which potentially means the availability of extension.
* The program/system is not performance oriented.
* The language is supported on Heroku, and also the website is easier to build and maintain.
### Server: Heroku (Temporary)
 Heroku is a PaaS platform, which allows us to operate a website without owning an actual server. 
### Website Framework: Python Flask
This framework is easy to build and extend. Also, this is the framework which I familiar with.
### Database: MongoDB (Temporary)
This is a noSQL db, the reason I choose this is because that it can store data with different scheme in a same collection (which can be considered table in SQL). It also provides a Python package for connecting between the program and the database. The biggest advantage is that their free plan already provided 512 MB storage, which I never used 5% of the storage they provided.

## Program Structure
We are going to create a few endpoints for different usage (The name and the structure of the endpoints are subject to change):
* [/index (Homepage)](#index)
* [/user](#user)
* [/admin](#admin)
* [/api](#api)
### /index
The main page of the website. which will have the button of accessing different functions or endpoints. 
### /user
The endpoint to access the other functions listed in [Pending Additional Function](#pending-additional-function). __Will not be used for now.__
### /admin
The endpoint to let the staffs control the appointment queue and other related things.
### /api
This is another portal to control the database of the system. The purpose of this is to let the existing application in use have access to the database if needed.

## Notes
* Ask Ray ([RaenonX JELLYCAT](https://shorelinecsclub.slack.com/messages/@UBB160092)) on Slack for program implementation details.
* If you want to join this project, please also contact Ray ([RaenonX JELLYCAT](https://shorelinecsclub.slack.com/messages/@UBB160092)) on Slack. Anyone want to join this project must join Shoreline CC CS Club. No requirements for joining the project.