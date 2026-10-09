<script lang="ts">
  // Imagem padrão dos contratos (static/avatar.jpg)
  export let size = 40;
</script>

<img
  src="/avatar.jpg"
  alt=""
  width={size}
  height={size}
  loading="lazy"
  class="shrink-0 rounded-full object-cover ring-1 ring-black/5 {$$props.class ?? ''}"
  style="width: {size}px; height: {size}px"
/>
