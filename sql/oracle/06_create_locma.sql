-- ============================================================
-- OracleDB - LOCMA (Location Master) Table DDL
-- Generated from: LOCMA_TABLE_ROW.xlsx
-- Columns: 44, Data rows: 16,695
-- ============================================================

CREATE TABLE LOCMA (
    WAREKY       NUMBER(10)       NOT NULL,
    LOCAKY       VARCHAR2(20)     NOT NULL,
    LOCATY       NUMBER(2)       ,
    SHORTX       VARCHAR2(100)   ,
    TASKTY       VARCHAR2(10)    ,
    ZONEKY       VARCHAR2(20)    ,
    AREAKY       VARCHAR2(20)    ,
    TKZONE       VARCHAR2(20)    ,
    FACLTY       VARCHAR2(10)    ,
    ARLVLL       VARCHAR2(10)    ,
    INDCPC       VARCHAR2(10)    ,
    INDTUT       VARCHAR2(10)    ,
    IBROUT       NUMBER(10)      ,
    OBROUT       NUMBER(10)      ,
    RPROUT       NUMBER(10)      ,
    STATUS       NUMBER(2)       ,
    ABCANV       VARCHAR2(10)    ,
    LENGTH       NUMBER(10)      ,
    WIDTHW       NUMBER(10)      ,
    HEIGHT       NUMBER(10)      ,
    CUBICM       NUMBER(10)      ,
    MAXCPC       NUMBER(10)      ,
    MAXQTY       NUMBER(10)      ,
    MAXWGT       NUMBER(10)      ,
    MAXLDR       NUMBER(10)      ,
    MAXSEC       NUMBER(10)      ,
    MIXSKU       VARCHAR2(10)    ,
    MIXLOT       VARCHAR2(10)    ,
    RPNCAT       VARCHAR2(10)    ,
    INDQTC       VARCHAR2(10)    ,
    QTYCHK       NUMBER(10)      ,
    NEDSID       VARCHAR2(10)    ,
    INDUPA       VARCHAR2(10)    ,
    INDUPK       VARCHAR2(10)    ,
    AUTLOC       VARCHAR2(10)    ,
    CREDAT       NUMBER(8)       ,
    CRETIM       NUMBER(6)       ,
    CREUSR       VARCHAR2(20)    ,
    LMODAT       NUMBER(8)       ,
    LMOTIM       NUMBER(6)       ,
    LMOUSR       VARCHAR2(20)    ,
    INDBZL       VARCHAR2(10)    ,
    INDARC       VARCHAR2(10)    ,
    UPDCHK       NUMBER(1)       
);

COMMENT ON TABLE LOCMA IS 'Location Master (지번 마스터)';

COMMENT ON COLUMN LOCMA.WAREKY       IS '거점';
COMMENT ON COLUMN LOCMA.LOCAKY       IS '지번';
COMMENT ON COLUMN LOCMA.LOCATY       IS '지번유형';
COMMENT ON COLUMN LOCMA.SHORTX       IS '지번명';
COMMENT ON COLUMN LOCMA.TASKTY       IS '작업타입';
COMMENT ON COLUMN LOCMA.ZONEKY       IS '구역';
COMMENT ON COLUMN LOCMA.AREAKY       IS '영역';
COMMENT ON COLUMN LOCMA.TKZONE       IS '작업구역';
COMMENT ON COLUMN LOCMA.FACLTY       IS '동/층';
COMMENT ON COLUMN LOCMA.ARLVLL       IS '창고레벨';
COMMENT ON COLUMN LOCMA.INDCPC       IS 'Capa체크';
COMMENT ON COLUMN LOCMA.INDTUT       IS '팔렛타입체크';
COMMENT ON COLUMN LOCMA.IBROUT       IS '입고순서';
COMMENT ON COLUMN LOCMA.OBROUT       IS '출고순서';
COMMENT ON COLUMN LOCMA.RPROUT       IS '보충순서';
COMMENT ON COLUMN LOCMA.STATUS       IS '상태';
COMMENT ON COLUMN LOCMA.ABCANV       IS 'ABC';
COMMENT ON COLUMN LOCMA.LENGTH       IS '길이';
COMMENT ON COLUMN LOCMA.WIDTHW       IS '가로';
COMMENT ON COLUMN LOCMA.HEIGHT       IS '높이';
COMMENT ON COLUMN LOCMA.CUBICM       IS 'CBM';
COMMENT ON COLUMN LOCMA.MAXCPC       IS '팔렛Capa.';
COMMENT ON COLUMN LOCMA.MAXQTY       IS '최대 수량';
COMMENT ON COLUMN LOCMA.MAXWGT       IS '최대 중량';
COMMENT ON COLUMN LOCMA.MAXLDR       IS 'Max rato';
COMMENT ON COLUMN LOCMA.MAXSEC       IS '최대 섹션수';
COMMENT ON COLUMN LOCMA.MIXSKU       IS '제품 혼적';
COMMENT ON COLUMN LOCMA.MIXLOT       IS 'Lot. 혼적';
COMMENT ON COLUMN LOCMA.RPNCAT       IS '보충유형';
COMMENT ON COLUMN LOCMA.INDQTC       IS '수량 체크 구분';
COMMENT ON COLUMN LOCMA.QTYCHK       IS '수량체크';
COMMENT ON COLUMN LOCMA.NEDSID       IS '섹션 아이디';
COMMENT ON COLUMN LOCMA.INDUPA       IS '적치가능';
COMMENT ON COLUMN LOCMA.INDUPK       IS '피킹가능';
COMMENT ON COLUMN LOCMA.AUTLOC       IS '자동창고 여부';
COMMENT ON COLUMN LOCMA.CREDAT       IS '생성일';
COMMENT ON COLUMN LOCMA.CRETIM       IS '생성시간';
COMMENT ON COLUMN LOCMA.CREUSR       IS '생성자';
COMMENT ON COLUMN LOCMA.LMODAT       IS '수정일';
COMMENT ON COLUMN LOCMA.LMOTIM       IS '수정시간';
COMMENT ON COLUMN LOCMA.LMOUSR       IS '수정자';
COMMENT ON COLUMN LOCMA.INDBZL       IS '비지니스로직';
COMMENT ON COLUMN LOCMA.INDARC       IS '아카이브 구분자';
COMMENT ON COLUMN LOCMA.UPDCHK       IS '수정체크';

-- ============================================================
-- Indexes
-- ============================================================

CREATE UNIQUE INDEX UK_LOCMA_WARE_LOCA ON LOCMA (WAREKY, LOCAKY);
CREATE INDEX IDX_LOCMA_ZONEKY ON LOCMA (ZONEKY);
CREATE INDEX IDX_LOCMA_AREAKY ON LOCMA (AREAKY);
CREATE INDEX IDX_LOCMA_STATUS ON LOCMA (STATUS);
CREATE INDEX IDX_LOCMA_TKZONE ON LOCMA (TKZONE);
CREATE INDEX IDX_LOCMA_LOCATY ON LOCMA (LOCATY);
