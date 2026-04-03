package com.company.module.inventory.dto;

import com.company.module.inventory.entity.ZonmaEntity;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ZonmaResponseDto {

    private Integer wareky;   // 거점
    private String zoneky;    // 구역
    private String zonety;    // 타입
    private String shortx;    // 명칭
    private String areaky;    // 영역
    private Integer credat;   // 생성일
    private Integer cretim;   // 생성시간
    private String creusr;    // 생성자
    private Integer lmodat;   // 수정일
    private Integer lmotim;   // 수정시간
    private String lmousr;    // 수정자
    private String indbzl;    // 지시정보
    private String indarc;    // 활서정보
    private Integer updchk;   // 갱신체크
    private String plntky;    // 플랜트
    private String stlky;     // 저장위치

    public static ZonmaResponseDto fromEntity(ZonmaEntity entity) {
        return ZonmaResponseDto.builder()
                .wareky(entity.getWareky())
                .zoneky(entity.getZoneky())
                .zonety(entity.getZonety())
                .shortx(entity.getShortx())
                .areaky(entity.getAreaky())
                .credat(entity.getCredat())
                .cretim(entity.getCretim())
                .creusr(entity.getCreusr())
                .lmodat(entity.getLmodat())
                .lmotim(entity.getLmotim())
                .lmousr(entity.getLmousr())
                .indbzl(entity.getIndbzl())
                .indarc(entity.getIndarc())
                .updchk(entity.getUpdchk())
                .plntky(entity.getPlntky())
                .stlky(entity.getStlky())
                .build();
    }
}
