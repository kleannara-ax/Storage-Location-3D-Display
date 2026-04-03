package com.company.module.inventory.controller;

import com.company.module.inventory.dto.ZonmaRequestDto;
import com.company.module.inventory.dto.ZonmaResponseDto;
import com.company.module.inventory.service.ZonmaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * ZONMA (Zone Master) REST Controller.
 * URL API Prefix: /inventory-api/zonma/**
 * No @Transactional here - transactions are managed in Service layer only.
 */
@RestController
@RequestMapping("/inventory-api/zonma")
@RequiredArgsConstructor
public class ZonmaController {

    private final ZonmaService zonmaService;

    // ============================================================
    // GET endpoints
    // ============================================================

    /** 전체 ZONMA 조회 */
    @GetMapping
    public ResponseEntity<List<ZonmaResponseDto>> findAll() {
        return ResponseEntity.ok(zonmaService.findAll());
    }

    /** 복합키(거점+구역) 단건 조회 */
    @GetMapping("/{wareky}/{zoneky}")
    public ResponseEntity<ZonmaResponseDto> findById(
            @PathVariable Integer wareky,
            @PathVariable String zoneky) {
        return ResponseEntity.ok(zonmaService.findById(wareky, zoneky));
    }

    /** 거점(WAREKY) 기준 조회 */
    @GetMapping("/wareky/{wareky}")
    public ResponseEntity<List<ZonmaResponseDto>> findByWareky(@PathVariable Integer wareky) {
        return ResponseEntity.ok(zonmaService.findByWareky(wareky));
    }

    /** 타입(ZONETY) 기준 조회 */
    @GetMapping("/zonety/{zonety}")
    public ResponseEntity<List<ZonmaResponseDto>> findByZonety(@PathVariable String zonety) {
        return ResponseEntity.ok(zonmaService.findByZonety(zonety));
    }

    /** 거점 + 타입 복합 조회 */
    @GetMapping("/wareky/{wareky}/zonety/{zonety}")
    public ResponseEntity<List<ZonmaResponseDto>> findByWarekyAndZonety(
            @PathVariable Integer wareky,
            @PathVariable String zonety) {
        return ResponseEntity.ok(zonmaService.findByWarekyAndZonety(wareky, zonety));
    }

    /** 영역(AREAKY) 기준 조회 */
    @GetMapping("/areaky/{areaky}")
    public ResponseEntity<List<ZonmaResponseDto>> findByAreaky(@PathVariable String areaky) {
        return ResponseEntity.ok(zonmaService.findByAreaky(areaky));
    }

    /** 플랜트(PLNTKY) 기준 조회 */
    @GetMapping("/plntky/{plntky}")
    public ResponseEntity<List<ZonmaResponseDto>> findByPlntky(@PathVariable String plntky) {
        return ResponseEntity.ok(zonmaService.findByPlntky(plntky));
    }

    /** 명칭(SHORTX) 키워드 검색 */
    @GetMapping("/search")
    public ResponseEntity<List<ZonmaResponseDto>> searchByShortx(
            @RequestParam String keyword) {
        return ResponseEntity.ok(zonmaService.searchByShortx(keyword));
    }

    /** 거점별 구역 수 통계 */
    @GetMapping("/stats/count-by-wareky")
    public ResponseEntity<List<Map<String, Object>>> countByWareky() {
        return ResponseEntity.ok(zonmaService.countByWareky());
    }

    // ============================================================
    // POST / PUT / DELETE endpoints
    // ============================================================

    /** 신규 ZONMA 등록 */
    @PostMapping
    public ResponseEntity<ZonmaResponseDto> create(
            @Valid @RequestBody ZonmaRequestDto requestDto) {
        ZonmaResponseDto created = zonmaService.create(requestDto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    /** ZONMA 수정 */
    @PutMapping("/{wareky}/{zoneky}")
    public ResponseEntity<ZonmaResponseDto> update(
            @PathVariable Integer wareky,
            @PathVariable String zoneky,
            @Valid @RequestBody ZonmaRequestDto requestDto) {
        return ResponseEntity.ok(zonmaService.update(wareky, zoneky, requestDto));
    }

    /** ZONMA 삭제 */
    @DeleteMapping("/{wareky}/{zoneky}")
    public ResponseEntity<Void> delete(
            @PathVariable Integer wareky,
            @PathVariable String zoneky) {
        zonmaService.delete(wareky, zoneky);
        return ResponseEntity.noContent().build();
    }
}
