package com.company.module.inventory.entity;

import jakarta.persistence.*;
import lombok.*;

/**
 * ZONMA Entity - Zone Master.
 * Table: ZONMA
 * Composite Key: WAREKY + ZONEKY
 * Mapped to OracleDB via inventoryEntityManagerFactory.
 */
@Entity
@Table(name = "ZONMA")
@IdClass(ZonmaId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ZonmaEntity {

    /** 거점 */
    @Id
    @Column(name = "WAREKY", nullable = false)
    private Integer wareky;

    /** 구역 */
    @Id
    @Column(name = "ZONEKY", nullable = false, length = 20)
    private String zoneky;

    /** 타입 */
    @Column(name = "ZONETY", length = 10)
    private String zonety;

    /** 명칭 */
    @Column(name = "SHORTX", length = 100)
    private String shortx;

    /** 영역 */
    @Column(name = "AREAKY", length = 20)
    private String areaky;

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

    /** 지시정보 */
    @Column(name = "INDBZL", length = 10)
    private String indbzl;

    /** 활서정보 */
    @Column(name = "INDARC", length = 10)
    private String indarc;

    /** 갱신체크 */
    @Column(name = "UPDCHK")
    private Integer updchk;

    /** 플랜트 */
    @Column(name = "PLNTKY", length = 10)
    private String plntky;

    /** 저장위치 */
    @Column(name = "STLKY", length = 10)
    private String stlky;
}
