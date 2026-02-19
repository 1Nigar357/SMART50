# SMART5🤓
#### Video Demo: https://youtu.be/yxg3NAgxW8k
#### Description:

<img width="2704" height="1466" alt="image" src="https://github.com/user-attachments/assets/41bf3de0-8f6c-42c3-81df-92e9f16ce5cc" />

# General Info About The Website

    SMART50 is designed to help students organize their schoolwork. Students can organize their homework and create a virtual
vocabulary with the help of SMART50. The design of the website is simple and neat at the same time. Every student has a portal which they access by logging in. There are two main web pages on this website: homework and vocabulary.

## Homework Web Page

    The homework web page contains a table where students can write down their homework. The table contains 4 columns: subject,
materials required, description, and deadline. In the subject column, the students choose the subject from which the homework was given from the select menu (e.g. math, physics, etc.). The column called materials required is where the students can write what is required to complete their homework. Hence, students will know what they need to take home when packing their bags. The other column called description is where the students write down what the homework is (e.g. read ten pages from the book, finish the worksheet, etc.). The last column called deadline is where students save the deadlines of the homework so that they stay aware of the upcoming homework deadline. As you add homework to the table, a button will appear next to the row created whose function is to delete the homework from the table and the database when completed.

## Vocabulary Web Page

    The second web page, vocabulary, is a virtual vocabulary where students can add words of their own choice. This web page contains
two buttons. One of which allows you to append a word manually by filling in all the required fields such as definition and part of speech. The other of which allows you to append the word automatically by just typing in the word. For automating this process, I used the web scrapping method. For this, I exploited three dictionaries: britannica (britannica.com), wordhippo (wordhippo.com), and yourdicitionary (yourdictionary.com). The words are displayed in flashcards composed of words, parts of speech, definitions, synonyms, antonyms, and sample sentences. Each flashcard comprises a button to delete the word from the database, thus, deleting the flashcard from the web page.


### Other Files

In project.db, I created three tables: users, homework, and vocab. In the templates folder, there are html codes for various web pages. In addition, I utilized some code from the cs50 (pset 9).









# SMART5🤓

## Summary 

    SMART5🤓 is a web application designed to display all the grades from various subjects in one centralized location. This allows students to check for grade updates with a single click, saving time by eliminating the need to check multiple portals individually. The application uses web scraping technique to collect grades from different university portals and stores them in one place. This collected information is then displayed in an organized manner for easy user reference.

## Instructions (User Guide)

The website user interface was made simple to make the navigation easier.

-   Enter your account 
    - Create an account by clicking the register section, if you dont have an account already
    - Login, if you do have account
-   Navigate to the Grades webpage using the toolbar located on the top of the website 
-   If you have not entered your school username and password previously
    -   Click the "Change Your School Account" button
    -   Enter your university username and password
-   Simply click the "Refresh" button and the program will do all the work for you and fetch your grades from the university portals
-   If you decide to change your school username and password
    -   Click the "Change Your School Account" button
    -   Enter your university username and password
-  When finished with your work, click the "Log Out" button in the toolbar


### Templates / Static (HTML / CSS)
This project includes HTML and CSS codes for the front-end portion of the project. In the templates folder, there are HTML codes for web pages of SMART5🤓. In the static folder, there is a CSS file used for styling the website. In addition, bootstrap is also used in this project for decoration and organization of the website elements 

### SQL Database
In project.db, there are four tables: users, school_accounts, sqlite_sequence, and grades. In the python code, these tables are modified and modified (data is added/deleted).  
