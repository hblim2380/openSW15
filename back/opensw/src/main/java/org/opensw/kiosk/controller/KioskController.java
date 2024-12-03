package org.opensw.kiosk.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.opensw.kiosk.entity.Menu;
import org.opensw.kiosk.entity.OrderRequest;
import org.opensw.kiosk.service.KioskService;
import org.springframework.http.*;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Controller
@Log4j2
@RequiredArgsConstructor
@RequestMapping("/page")
public class KioskController {

    private final KioskService kioskService;

    @GetMapping("/start")
    public String start() {
        log.info("start kiosk...............");

        return "kiosk/start";
    }

    @GetMapping("/get")
    public String getKioskList(Model model) {

        log.info("get all kiosk items...........");

        List<Menu> allKiosks = kioskService.getAllKiosks();

        model.addAttribute("allKiosks", allKiosks);

        return "kiosk/main";
    }

    @ResponseBody
    @PostMapping("/order")
    public ResponseEntity<String> order(@RequestBody OrderRequest orderRequest) {
        log.info("Processing orders...");

        try {
            // 여러 개의 주문 처리
            kioskService.saveOrder(orderRequest);
            log.info("Order saved: {}", orderRequest);

            return ResponseEntity.ok("Orders processed successfully");
        } catch (Exception e) {
            log.error("Error processing orders: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error processing orders");
        }
    }
    /*@PostMapping("/list/detect")
    public ResponseEntity<Map<String, String>> detectAge(@RequestBody Map<String, String> request) {
        String base64Image = request.get("image");

        // 외부 API로 이미지 전송
        String ageGroup = sendImageToExternalApi(base64Image);

        // 응답 생성
        Map<String, String> response = new HashMap<>();
        response.put("ageGroup", ageGroup); // 예: elderly, child, adult
        return ResponseEntity.ok(response);
    }

    private String sendImageToExternalApi(String base64Image) {
        // 외부 API 요청 로직 (HTTP POST)
        RestTemplate restTemplate = new RestTemplate();
        String apiUrl = "https://localhost:8081/detect";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> body = new HashMap<>();
        body.put("image", base64Image);

        HttpEntity<Map<String, String>> request = new HttpEntity<>(body, headers);
        ResponseEntity<Map> response = restTemplate.exchange(apiUrl, HttpMethod.POST, request, Map.class);

        // 결과에서 ageGroup 추출
        return (String) response.getBody().get("ageGroup");
    }*/

}
