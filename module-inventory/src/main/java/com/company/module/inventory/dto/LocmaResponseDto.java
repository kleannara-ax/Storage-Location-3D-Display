package com.company.module.inventory.dto;

import com.company.module.inventory.entity.LocmaEntity;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LocmaResponseDto {

    private Integer wareky;   // 거점
    private String locaky;    // 지번
    private Integer locaty;   // 지번유형
    private String shortx;    // 지번명
    private String taskty;    // 작업타입
    private String zoneky;    // 구역
    private String areaky;    // 영역
    private String tkzone;    // 작업구역
    private String faclty;    // 동/층
    private String arlvll;    // 창고레벨
    private String indcpc;    // Capa체크
    private String indtut;    // 팔렛타입체크
    private Long ibrout;      // 입고순서
    private Long obrout;      // 출고순서
    private Long rprout;      // 보충순서
    private Integer status;   // 상태
    private String abcanv;    // ABC
    private Long length;      // 길이
    private Long widthw;      // 가로
    private Long height;      // 높이
    private Long cubicm;      // CBM
    private Long maxcpc;      // 팔렛Capa
    private Long maxqty;      // 최대 수량
    private Long maxwgt;      // 최대 중량
    private Long maxldr;      // Max rato
    private Long maxsec;      // 최대 섹션수
    private String mixsku;    // 제품 혼적
    private String mixlot;    // Lot 혼적
    private String rpncat;    // 보충유형
    private String indqtc;    // 수량 체크 구분
    private Long qtychk;      // 수량체크
    private String nedsid;    // 섹션 아이디
    private String indupa;    // 적치가능
    private String indupk;    // 피킹가능
    private String autloc;    // 자동창고 여부
    private Integer credat;   // 생성일
    private Integer cretim;   // 생성시간
    private String creusr;    // 생성자
    private Integer lmodat;   // 수정일
    private Integer lmotim;   // 수정시간
    private String lmousr;    // 수정자
    private String indbzl;    // 비지니스로직
    private String indarc;    // 아카이브 구분자
    private Integer updchk;   // 수정체크

    public static LocmaResponseDto fromEntity(LocmaEntity e) {
        return LocmaResponseDto.builder()
                .wareky(e.getWareky())
                .locaky(e.getLocaky())
                .locaty(e.getLocaty())
                .shortx(e.getShortx())
                .taskty(e.getTaskty())
                .zoneky(e.getZoneky())
                .areaky(e.getAreaky())
                .tkzone(e.getTkzone())
                .faclty(e.getFaclty())
                .arlvll(e.getArlvll())
                .indcpc(e.getIndcpc())
                .indtut(e.getIndtut())
                .ibrout(e.getIbrout())
                .obrout(e.getObrout())
                .rprout(e.getRprout())
                .status(e.getStatus())
                .abcanv(e.getAbcanv())
                .length(e.getLength())
                .widthw(e.getWidthw())
                .height(e.getHeight())
                .cubicm(e.getCubicm())
                .maxcpc(e.getMaxcpc())
                .maxqty(e.getMaxqty())
                .maxwgt(e.getMaxwgt())
                .maxldr(e.getMaxldr())
                .maxsec(e.getMaxsec())
                .mixsku(e.getMixsku())
                .mixlot(e.getMixlot())
                .rpncat(e.getRpncat())
                .indqtc(e.getIndqtc())
                .qtychk(e.getQtychk())
                .nedsid(e.getNedsid())
                .indupa(e.getIndupa())
                .indupk(e.getIndupk())
                .autloc(e.getAutloc())
                .credat(e.getCredat())
                .cretim(e.getCretim())
                .creusr(e.getCreusr())
                .lmodat(e.getLmodat())
                .lmotim(e.getLmotim())
                .lmousr(e.getLmousr())
                .indbzl(e.getIndbzl())
                .indarc(e.getIndarc())
                .updchk(e.getUpdchk())
                .build();
    }
}
