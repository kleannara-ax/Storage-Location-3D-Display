package com.company.module.inventory.entity;

import lombok.*;

import java.io.Serializable;

/**
 * Composite Primary Key for LOCMA table.
 * WAREKY (거점) + LOCAKY (지번)
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode
public class LocmaId implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 거점 */
    private Integer wareky;

    /** 지번 */
    private String locaky;
}
