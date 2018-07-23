<template>
  <div class="po-ranklist">
  </div>
</template>

<script>
var NProgress = window.NProgress

export default {
  name: 'RankList',
  data () {
    return {
      NaN
    }
  },
  route: {
    waitForData: true,
    data: function (transition) {
      NProgress.start()
      NProgress.set(0.6)
      NProgress.done()
      transition.next({})
    }
  },
  methods: {
    NaN
  },
  ready: function () {
    NaN
  },
  components: {
    NaN
  }
}
</script>

<style lang='less'>

.po-ranklist {
}

</style>
