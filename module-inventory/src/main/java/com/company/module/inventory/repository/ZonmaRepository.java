package com.company.module.inventory.repository;

import com.company.module.inventory.entity.ZonmaEntity;
import com.company.module.inventory.entity.ZonmaId;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ZonmaRepository extends JpaRepository<ZonmaEntity, ZonmaId> {

    /** 거점(WAREKY) 기준 조회 */
    List<ZonmaEntity> findByWareky(Integer wareky);

    /** 타입(ZONETY) 기준 조회 */
    List<ZonmaEntity> findByZonety(String zonety);

    /** 영역(AREAKY) 기준 조회 */
    List<ZonmaEntity> findByAreaky(String areaky);

    /** 거점 + 타입 복합 조회 */
    List<ZonmaEntity> findByWarekyAndZonety(Integer wareky, String zonety);

    /** 플랜트 기준 조회 */
    List<ZonmaEntity> findByPlntky(String plntky);

    /** 명칭 키워드 검색 */
    @Query("SELECT z FROM ZonmaEntity z WHERE z.shortx LIKE %:keyword%")
    List<ZonmaEntity> searchByShortx(@Param("keyword") String keyword);

    /** 거점별 구역 수 조회 */
    @Query("SELECT z.wareky, COUNT(z) FROM ZonmaEntity z GROUP BY z.wareky ORDER BY z.wareky")
    List<Object[]> countByWareky();
}
