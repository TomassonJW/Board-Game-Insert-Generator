import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.github.skjolber.packing.api.Box;
import com.github.skjolber.packing.api.BoxItem;
import com.github.skjolber.packing.api.BoxStackValue;
import com.github.skjolber.packing.api.Container;
import com.github.skjolber.packing.api.ContainerItem;
import com.github.skjolber.packing.api.PackagerResult;
import com.github.skjolber.packing.api.Placement;
import com.github.skjolber.packing.packer.laff.FastLargestAreaFitFirstPackager;

public final class LaffFloorWorker {
    private static final String INPUT_HEADER = "P64L07FLOOR\t1";
    private static final String OUTPUT_HEADER = "P64L07RESULT\t1";

    private static final class Item {
        final String id;
        final int width;
        final int height;

        Item(String id, int width, int height) {
            this.id = id;
            this.width = width;
            this.height = height;
        }
    }

    private static String decodeId(String value) {
        int padding = (4 - value.length() % 4) % 4;
        return new String(
            Base64.getUrlDecoder().decode(value + "=".repeat(padding)),
            StandardCharsets.UTF_8
        );
    }

    private static String encodeId(String value) {
        return Base64.getUrlEncoder()
            .withoutPadding()
            .encodeToString(value.getBytes(StandardCharsets.UTF_8));
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new IllegalArgumentException("Expected input and output paths.");
        }
        List<String> lines = Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8);
        if (lines.size() < 5 || !INPUT_HEADER.equals(lines.get(0))) {
            throw new IllegalArgumentException("Unsupported floor worker input.");
        }
        String[] bin = lines.get(1).split("\t");
        String[] limit = lines.get(2).split("\t");
        String[] rotation = lines.get(3).split("\t");
        if (!"BIN".equals(bin[0]) || !"LIMIT".equals(limit[0]) || !"ROTATE".equals(rotation[0])) {
            throw new IllegalArgumentException("Incomplete floor worker input.");
        }
        int binWidth = Integer.parseInt(bin[1]);
        int binHeight = Integer.parseInt(bin[2]);
        boolean rotationAllowed = "1".equals(rotation[1]);
        List<Item> items = new ArrayList<>();
        List<BoxItem> boxes = new ArrayList<>();
        Map<String, Item> byId = new HashMap<>();
        for (int index = 4; index < lines.size(); index++) {
            String[] row = lines.get(index).split("\t");
            if (row.length != 4 || !"ITEM".equals(row[0])) {
                throw new IllegalArgumentException("Invalid floor item.");
            }
            Item item = new Item(decodeId(row[1]), Integer.parseInt(row[2]), Integer.parseInt(row[3]));
            if (byId.put(item.id, item) != null) {
                throw new IllegalArgumentException("Duplicate floor item.");
            }
            items.add(item);
            Box.Builder builder = Box.newBuilder()
                .withId(item.id)
                .withSize(item.width, item.height, 1)
                .withWeight(1);
            if (rotationAllowed) {
                builder.withRotate2D();
            } else {
                builder.withRotation(
                    com.github.skjolber.packing.api.Rotation
                        .newBuilder()
                        .withBottomAtZeroDegrees()
                        .build()
                );
            }
            boxes.add(new BoxItem(builder.build(), 1));
        }
        Container container = Container.newBuilder()
            .withId("bgig-floor")
            .withSize(binWidth, binHeight, 1)
            .withMaxLoadWeight(items.size())
            .build();
        FastLargestAreaFitFirstPackager packager = FastLargestAreaFitFirstPackager
            .newBuilder()
            .build();
        long started = System.nanoTime();
        PackagerResult result = packager.newResultBuilder()
            .withBoxItems(boxes)
            .withContainerItem(new ContainerItem(container, 1))
            .withMaxContainerCount(1)
            .build();
        double solveMs = (System.nanoTime() - started) / 1_000_000.0;
        List<String> output = new ArrayList<>();
        output.add(OUTPUT_HEADER);
        if (!result.isSuccess()) {
            output.add("RESULT\tunknown\t" + solveMs + "\t" + encodeId("no_complete_pack"));
        } else {
            output.add("RESULT\tfeasible\t" + solveMs + "\t" + encodeId("complete_pack"));
            for (Placement placement : result.get(0).getStack().getPlacements()) {
                String id = placement.getBox().getId();
                Item item = byId.get(id);
                BoxStackValue value = placement.getStackValue();
                int degrees = value.getDx() == item.width && value.getDy() == item.height ? 0 : 90;
                output.add(
                    "PLACEMENT\t" + encodeId(id)
                    + "\t" + placement.getAbsoluteX()
                    + "\t" + placement.getAbsoluteY()
                    + "\t" + degrees
                );
            }
            output.add("METRIC\tcontainers\t" + result.size());
        }
        Path target = Path.of(args[1]);
        Path temporary = Path.of(args[1] + ".tmp");
        Files.write(temporary, output, StandardCharsets.UTF_8);
        Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING);
        packager.close();
    }
}
