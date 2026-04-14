package com.company.module.inventory.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LocmaRequestDto {

    @NotNull(message = "거점(WAREKY)은 필수입니다")
    private Integer wareky;

    @NotBlank(message = "지번(LOCAKY)은 필수입니다")
    @Size(max = 20)
    private String locaky;

    private Integer locaty;

    @Size(max = 100)
    private String shortx;

    @Size(max = 10)
    private String taskty;

    @Size(max = 20)
    private String zoneky;

    @Size(max = 20)
    private String areaky;

    @Size(max = 20)
    private String tkzone;

    @Size(max = 10)
    private String faclty;

    @Size(max = 10)
    private String arlvll;

    @Size(max = 10)
    private String indcpc;

    @Size(max = 10)
    private String indtut;

    private Long ibrout;
    private Long obrout;
    private Long rprout;
    private Integer status;

    @Size(max = 10)
    private String abcanv;

    private Long length;
    private Long widthw;
    private Long height;
    private Long cubicm;
    private Long maxcpc;
    private Long maxqty;
    private Long maxwgt;
    private Long maxldr;
    private Long maxsec;

    @Size(max = 10)
    private String mixsku;

    @Size(max = 10)
    private String mixlot;

    @Size(max = 10)
    private String rpncat;

    @Size(max = 10)
    private String indqtc;

    private Long qtychk;

    @Size(max = 10)
    private String nedsid;

    @Size(max = 10)
    private String indupa;

    @Size(max = 10)
    private String indupk;

    @Size(max = 10)
    private String autloc;

    private Integer credat;
    private Integer cretim;

    @Size(max = 20)
    private String creusr;

    private Integer lmodat;
    private Integer lmotim;

    @Size(max = 20)
    private String lmousr;

    @Size(max = 10)
    private String indbzl;

    @Size(max = 10)
    private String indarc;

    private Integer updchk;
}
