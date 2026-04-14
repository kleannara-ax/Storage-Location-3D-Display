-- ============================================================
-- OracleDB - ZONMA Table DDL
-- Generated from: ZONMA_TABLE_ROW.xlsx
-- Data rows: 368
-- ============================================================

CREATE TABLE ZONMA (
    WAREKY           NUMBER(10)       NOT NULL,
    ZONEKY           VARCHAR2(20)     NOT NULL,
    ZONETY           VARCHAR2(10)    ,
    SHORTX           VARCHAR2(100)   ,
    AREAKY           VARCHAR2(20)    ,
    CREDAT           NUMBER(8)       ,
    CRETIM           NUMBER(6)       ,
    CREUSR           VARCHAR2(20)    ,
    LMODAT           NUMBER(8)       ,
    LMOTIM           NUMBER(6)       ,
    LMOUSR           VARCHAR2(20)    ,
    INDBZL           VARCHAR2(10)    ,
    INDARC           VARCHAR2(10)    ,
    UPDCHK           NUMBER(1)       ,
    PLNTKY           VARCHAR2(10)    ,
    STLKY            VARCHAR2(10)    
);

COMMENT ON COLUMN ZONMA.WAREKY           IS '거점';
COMMENT ON COLUMN ZONMA.ZONEKY           IS '구역';
COMMENT ON COLUMN ZONMA.ZONETY           IS '타입';
COMMENT ON COLUMN ZONMA.SHORTX           IS '명칭';
COMMENT ON COLUMN ZONMA.AREAKY           IS '영역';
COMMENT ON COLUMN ZONMA.CREDAT           IS '생성일';
COMMENT ON COLUMN ZONMA.CRETIM           IS '생성시간';
COMMENT ON COLUMN ZONMA.CREUSR           IS '생성자';
COMMENT ON COLUMN ZONMA.LMODAT           IS '수정일';
COMMENT ON COLUMN ZONMA.LMOTIM           IS '수정시간';
COMMENT ON COLUMN ZONMA.LMOUSR           IS '수정자';
COMMENT ON COLUMN ZONMA.INDBZL           IS '지시정보';
COMMENT ON COLUMN ZONMA.INDARC           IS '활서정보';
COMMENT ON COLUMN ZONMA.UPDCHK           IS '갱신체크';
COMMENT ON COLUMN ZONMA.PLNTKY           IS '플랜트';
COMMENT ON COLUMN ZONMA.STLKY            IS '저장위치';

-- ============================================================
-- Indexes (composite key: WAREKY + ZONEKY)
-- ============================================================

CREATE UNIQUE INDEX UK_ZONMA_WARE_ZONE ON ZONMA (WAREKY, ZONEKY);
CREATE INDEX IDX_ZONMA_ZONETY ON ZONMA (ZONETY);
CREATE INDEX IDX_ZONMA_AREAKY ON ZONMA (AREAKY);
CREATE INDEX IDX_ZONMA_PLNTKY ON ZONMA (PLNTKY);
