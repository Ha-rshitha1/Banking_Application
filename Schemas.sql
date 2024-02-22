use Banking_App;
CREATE TABLE users (
    username VARCHAR(255),
    address VARCHAR(255),
    aadhar BIGINT(16),
    mobile BIGINT(20),
    balance INT,
    account_number BIGINT(20),
    password VARCHAR(12),
    credit_card_number BIGINT(20),
    credit_card_pin INT(6),
    credit_card_cvv INT(5),
    debit_card_number BIGINT(20),
    debit_card_pin INT(6),
    debit_card_cvv INT(5)
);




use Banking_App;
CREATE TABLE cards (
    username VARCHAR(255) NOT NULL,
    card_type VARCHAR(10) NOT NULL,
    card_number BIGINT(20) NOT NULL,
    pin INT(4) NOT NULL,
    cvv INT(3) NOT NULL

);


use Banking_App;
CREATE TABLE beneficiaries (
    name VARCHAR(255) NOT NULL,
    account_number BIGINT(20) NOT NULL,
    username VARCHAR(255) NOT NULL
);
