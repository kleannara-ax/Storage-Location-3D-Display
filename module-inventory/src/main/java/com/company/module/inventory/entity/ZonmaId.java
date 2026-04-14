package com.company.module.inventory.entity;

import lombok.*;

import java.io.Serializable;

/**
 * Composite Primary Key for ZONMA table.
 * WAREKY (거점) + ZONEKY (구역)
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
public class ZonmaId implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 거점 */
    private Integer wareky;

    /** 구역 */
    private String zoneky;
}
