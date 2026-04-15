CREATE TABLE IF NOT EXISTS stocks (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    symbol           VARCHAR(20)    NOT NULL,
    name             VARCHAR(100)   NOT NULL,
    sector           VARCHAR(10)    NOT NULL,
    currency         VARCHAR(3)     NOT NULL,
    initial_value    DECIMAL(12,4)  NOT NULL,
    initial_quantity INT            NOT NULL DEFAULT 0,
    initial_date     DATE           NOT NULL,
    upper_threshold  DECIMAL(12,4)  NOT NULL DEFAULT -1,
    lower_threshold  DECIMAL(12,4)  NOT NULL DEFAULT -1,
    purchase_fee     DECIMAL(10,4)  NULL,
    sold             TINYINT(1)     NOT NULL DEFAULT 0,
    sell_date        DATE           NULL,
    INDEX idx_symbol (symbol),
    INDEX idx_sold   (sold)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
