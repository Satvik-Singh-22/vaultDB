-- Enable UUID extension for CardNumber

---------------------------------------------------------------
-- 1. Create Branch Table 
---------------------------------------------------------------
CREATE TABLE Branch (
    BranchID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Location VARCHAR(200) NOT NULL
);

---------------------------------------------------------------
-- 2. Create Employee Table
---------------------------------------------------------------
CREATE TABLE Employee (
    EmployeeID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    BranchID INT REFERENCES Branch(BranchID), 
    Role VARCHAR(50), 
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(256) NOT NULL
);

---------------------------------------------------------------
-- 3. Create BankManager Table
---------------------------------------------------------------
CREATE TABLE BankManager (
    ManagerID INT PRIMARY KEY REFERENCES Employee(EmployeeID) ON DELETE CASCADE,
    BranchID INT UNIQUE REFERENCES Branch(BranchID) ON DELETE CASCADE
);

---------------------------------------------------------------
-- 4. Create Customer Table
---------------------------------------------------------------
CREATE TABLE Customer (
    CustomerID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(200),
    PhoneNumber VARCHAR(25),
    Email VARCHAR(100) UNIQUE,
    DateOfBirth DATE,
    BranchID INT REFERENCES Branch(BranchID)
);

---------------------------------------------------------------
-- 5. Create AccountType Table (Before Account)
---------------------------------------------------------------
CREATE TABLE AccountType (
    TypeID SERIAL PRIMARY KEY,
    TypeName VARCHAR(20) UNIQUE NOT NULL,
    InterestRate DECIMAL(5,2) NOT NULL
);

---------------------------------------------------------------
-- 6. Create Account Table
---------------------------------------------------------------
CREATE TABLE Account (
    AccountID SERIAL PRIMARY KEY,
    TypeID INT REFERENCES AccountType(TypeID),
    Balance DECIMAL(15,2) DEFAULT 0.00,
    CustomerID INT REFERENCES Customer(CustomerID),
    BranchID INT REFERENCES Branch(BranchID)
);

---------------------------------------------------------------
-- 7. Create LoanType Table
---------------------------------------------------------------
CREATE TABLE LoanType (
    Code SERIAL PRIMARY KEY,
    Name VARCHAR(50) UNIQUE NOT NULL,
    InterestRate DECIMAL(5,2) NOT NULL
);

---------------------------------------------------------------
-- 8. Create Loan Table
---------------------------------------------------------------
CREATE TABLE Loan (
    LoanID SERIAL PRIMARY KEY,
    Type INT REFERENCES LoanType(Code),
    LoanAmount DECIMAL(15,2) NOT NULL,
    StartDate DATE DEFAULT CURRENT_DATE,
    Tenure INT CHECK (Tenure > 0),
    CustomerID INT REFERENCES Customer(CustomerID),
    EmployeeID INT REFERENCES Employee(EmployeeID),
    Status VARCHAR(20) CHECK (Status IN ('Approved', 'Pending', 'Repaid', 'Overdue'))
);

---------------------------------------------------------------
-- 9. Create Repayment Table
---------------------------------------------------------------
CREATE TABLE Repayment (
    RepaymentID SERIAL PRIMARY KEY,
    LoanID INT REFERENCES Loan(LoanID),
    CustomerID INT REFERENCES Customer(CustomerID),
    DueDate DATE NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Status VARCHAR(20) CHECK (Status IN ('Pending', 'Paid', 'Overdue')),
    PaymentDate DATE
);

---------------------------------------------------------------
-- 10. Create BankTransaction Table
---------------------------------------------------------------
CREATE TABLE BankTransaction (
    TransactionID SERIAL PRIMARY KEY,
    TransactionType VARCHAR(20) CHECK (TransactionType IN ('Deposit', 'Withdrawal', 'Transfer')),
    Amount DECIMAL(15,2) NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    AccountID INT REFERENCES Account(AccountID),
    ReceiverAccountID INT REFERENCES Account(AccountID) ON DELETE SET NULL,  -- Fix circular reference
    EmployeeID INT DEFAULT NULL REFERENCES Employee(EmployeeID),
    Status VARCHAR(20) CHECK (Status IN ('Failed', 'Successful', 'Pending'))
);

---------------------------------------------------------------
-- 11. Create Card Table
---------------------------------------------------------------
CREATE TABLE Card (
    CardID SERIAL PRIMARY KEY,
    CardNumber UUID,
    ExpiryDate DATE NOT NULL,
    CardType VARCHAR(10) CHECK (CardType IN ('Debit', 'Credit')),
    AccountID INT REFERENCES Account(AccountID) ON DELETE CASCADE
);

---------------------------------------------------------------
-- 12. Create CustomerSupport Table
---------------------------------------------------------------
CREATE TABLE CustomerSupport (
    SupportID SERIAL PRIMARY KEY,
    CustomerID INT REFERENCES Customer(CustomerID),
    IssueDescription VARCHAR(500),
    Status VARCHAR(20) CHECK (Status IN ('Open', 'In Progress', 'Resolved')),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ResolvedAt TIMESTAMP
);
