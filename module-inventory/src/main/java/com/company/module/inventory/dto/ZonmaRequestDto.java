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
public class ZonmaRequestDto {

    @NotNull(message = "거점(WAREKY)은 필수입니다")
    private Integer wareky;

    @NotBlank(message = "구역(ZONEKY)은 필수입니다")
    @Size(max = 20, message = "구역(ZONEKY)은 20자 이하여야 합니다")
    private String zoneky;

    @Size(max = 10, message = "타입(ZONETY)은 10자 이하여야 합니다")
    private String zonety;

    @Size(max = 100, message = "명칭(SHORTX)은 100자 이하여야 합니다")
    private String shortx;

    @Size(max = 20, message = "영역(AREAKY)은 20자 이하여야 합니다")
    private String areaky;

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

    @Size(max = 10)
    private String plntky;

    @Size(max = 10)
    private String stlky;
}
