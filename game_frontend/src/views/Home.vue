<template>
  <div class="container-fluid h-100">
    <div class="row h-100">
      <div class="col h-100 py-3">
        <div
          class="h-100 w-100 d-flex justify-content-center align-items-center"
          ref="parent"
        >
          <div id="playfield" ref="playfield"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import io from "socket.io-client";
import SVG from "svg.js";

const WIDTH = 1000;
const HEIGHT = 1000;

export default {
  name: "home",
  components: {},
  data() {
    return {
      gameState: [],
      widthActual: 1000,
      heightActual: 1000
    };
  },
  mounted() {
    const server = prompt("server ip");
    console.log(server);
    this.socket = io(server);
    this.socket.on("state", this.state_update);

    this.playfield = SVG("playfield");

    window.addEventListener("resize", this.handle_resize);
    this.handle_resize();
  },
  methods: {
    state_update(gameState) {
      this.gameState = gameState;
      this.draw();
    },
    draw() {
      this.playfield.clear();
      // this.playfield
      //   .rect(this.convertXToActual(1000), this.convertYToActual(1000))
      //   .attr({
      //     stroke: "#e74c3c",
      //     "stroke-width": 5,
      //     "stroke-alignment": "outer",
      //     fill: "none"
      //   });

      for (let blob of this.gameState) {
        if (blob.is_food) {
          this.playfield
            .circle(this.convertXToActual(blob.radius * 2))
            .cx(this.convertXToActual(blob.coords[0]))
            .cy(this.convertYToActual(blob.coords[1]))
            .attr("fill", "grey");
          continue;
        }

        this.playfield
          .circle(this.convertXToActual(blob.radius * 2))
          .cx(this.convertXToActual(blob.coords[0]))
          .cy(this.convertYToActual(blob.coords[1]))
          .attr("fill", "#e74c3c");

        this.playfield
          .text(blob.owner_name)
          .cx(this.convertXToActual(blob.coords[0]))
          .cy(this.convertYToActual(blob.coords[1] - blob.radius))
          .attr({
            size: 5
          });
      }
    },
    handle_resize() {
      if (this.$refs.playfield) {
        this.$refs.playfield.style.display = "none";
      }
      this.$nextTick(() => {
        let min = Math.min(
          this.$refs.parent.offsetWidth,
          this.$refs.parent.offsetHeight
        );
        this.$refs.playfield.style.width = min + "px";
        this.$refs.playfield.style.height = min + "px";
        this.$refs.playfield.style.display = "block";

        this.widthActual = min;
        this.heightActual = min;
      });
    },

    convertXToActual(value) {
      return (value / WIDTH) * this.widthActual;
    },
    convertYToActual(value) {
      return (value / HEIGHT) * this.heightActual;
    }
  }
};
</script>

<style scoped>
#playfield {
  outline: solid 3px grey;
}
</style>
