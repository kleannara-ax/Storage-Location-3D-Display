package com.company.module.inventory.entity;

import jakarta.persistence.*;
import lombok.*;

/**
 * LOCMA Entity - Location Master (지번 마스터).
 * Table: LOCMA (44 columns)
 * Composite Key: WAREKY + LOCAKY
 * Mapped to OracleDB via inventoryEntityManagerFactory.
 */
@Entity
@Table(name = "LOCMA")
@IdClass(LocmaId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LocmaEntity {

    /** 거점 */
    @Id
    @Column(name = "WAREKY", nullable = false)
    private Integer wareky;

    /** 지번 */
    @Id
    @Column(name = "LOCAKY", nullable = false, length = 20)
    private String locaky;

    /** 지번유형 */
    @Column(name = "LOCATY")
    private Integer locaty;

    /** 지번명 */
    @Column(name = "SHORTX", length = 100)
    private String shortx;

    /** 작업타입 */
    @Column(name = "TASKTY", length = 10)
    private String taskty;

    /** 구역 */
    @Column(name = "ZONEKY", length = 20)
    private String zoneky;

    /** 영역 */
    @Column(name = "AREAKY", length = 20)
    private String areaky;

    /** 작업구역 */
    @Column(name = "TKZONE", length = 20)
    private String tkzone;

    /** 동/층 */
    @Column(name = "FACLTY", length = 10)
    private String faclty;

    /** 창고레벨 */
    @Column(name = "ARLVLL", length = 10)
    private String arlvll;

    /** Capa체크 */
    @Column(name = "INDCPC", length = 10)
    private String indcpc;

    /** 팔렛타입체크 */
    @Column(name = "INDTUT", length = 10)
    private String indtut;

    /** 입고순서 */
    @Column(name = "IBROUT")
    private Long ibrout;

    /** 출고순서 */
    @Column(name = "OBROUT")
    private Long obrout;

    /** 보충순서 */
    @Column(name = "RPROUT")
    private Long rprout;

    /** 상태 */
    @Column(name = "STATUS")
    private Integer status;

    /** ABC */
    @Column(name = "ABCANV", length = 10)
    private String abcanv;

    /** 길이 */
    @Column(name = "LENGTH")
    private Long length;

    /** 가로 */
    @Column(name = "WIDTHW")
    private Long widthw;

    /** 높이 */
    @Column(name = "HEIGHT")
    private Long height;

    /** CBM */
    @Column(name = "CUBICM")
    private Long cubicm;

    /** 팔렛Capa. */
    @Column(name = "MAXCPC")
    private Long maxcpc;

    /** 최대 수량 */
    @Column(name = "MAXQTY")
    private Long maxqty;

    /** 최대 중량 */
    @Column(name = "MAXWGT")
    private Long maxwgt;

    /** Max rato */
    @Column(name = "MAXLDR")
    private Long maxldr;

    /** 최대 섹션수 */
    @Column(name = "MAXSEC")
    private Long maxsec;

    /** 제품 혼적 */
    @Column(name = "MIXSKU", length = 10)
    private String mixsku;

    /** Lot. 혼적 */
    @Column(name = "MIXLOT", length = 10)
    private String mixlot;

    /** 보충유형 */
    @Column(name = "RPNCAT", length = 10)
    private String rpncat;

    /** 수량 체크 구분 */
    @Column(name = "INDQTC", length = 10)
    private String indqtc;

    /** 수량체크 */
    @Column(name = "QTYCHK")
    private Long qtychk;

    /** 섹션 아이디 */
    @Column(name = "NEDSID", length = 10)
    private String nedsid;

    /** 적치가능 */
    @Column(name = "INDUPA", length = 10)
    private String indupa;

    /** 피킹가능 */
    @Column(name = "INDUPK", length = 10)
    private String indupk;

    /** 자동창고 여부 */
    @Column(name = "AUTLOC", length = 10)
    private String autloc;

    /** 생성일 */
    @Column(name = "CREDAT")
    private Integer credat;

    /** 생성시간 */
    @Column(name = "CRETIM")
    private Integer cretim;

    /** 생성자 */
    @Column(name = "CREUSR", length = 20)
    private String creusr;

    /** 수정일 */
    @Column(name = "LMODAT")
    private Integer lmodat;

    /** 수정시간 */
    @Column(name = "LMOTIM")
    private Integer lmotim;

    /** 수정자 */
    @Column(name = "LMOUSR", length = 20)
    private String lmousr;

    /** 비지니스로직 */
    @Column(name = "INDBZL", length = 10)
    private String indbzl;

    /** 아카이브 구분자 */
    @Column(name = "INDARC", length = 10)
    private String indarc;

    /** 수정체크 */
    @Column(name = "UPDCHK")
    private Integer updchk;
}
