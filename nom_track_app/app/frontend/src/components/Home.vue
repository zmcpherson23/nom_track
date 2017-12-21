<template>
  <div>
    <h1>Nom Track</h1>
    <h4 class="font-italic">Your one stop shop for everything lunch around the Howard Hughes Center in Los Angeles</h4>
    <h4 class="mt-md-5 text-info font-weight-bold">Food Options for: {{ todaysFoodOptions.date  }}</h4>

    <div class="mt-3">
      <b-card-group deck class="mb-3 mx-auto d-flex justify-content-center">

    <div v-for="foodOption in todaysFoodOptions.food_sources">
      <b-card :title="foodOption.name"
              :img-src="foodOption.yelp_info.image_url.replace('/o.jpg', '/348s.jpg') || 'https://lorempixel.com/350/350/food/5/'"
              img-alt="Image"
              img-top
              tag="article"
              style="max-width: 24rem; min-height: 30rem; max-height: 50rem; overflow: hidden"
              class="mb-2">
        <div>
          <div class="card-text">
            <b>Price Range:</b> {{ foodOption.yelp_info.cost }}
          </div>
          <div v-if="foodOption.yelp_info.rating" class="card-text">
            <b>Yelp Rating:</b> {{ foodOption.yelp_info.rating }}
          </div>
          <div v-if="foodOption.yelp_info.number_of_reviews" class="card-text">
            <b># of Yelp Reviews:</b> {{ foodOption.yelp_info.number_of_reviews }}
          </div>
          <div class="card-text">
            <b>Closes at: </b>{{ foodOption.hours.close }}
            <!--<div v-if="now ">{{ foodOption.hours.close }} </div>-->
          </div>
        </div>
        <b-button class="mt-2 mb-2" :href="foodOption.menu" variant="primary">Menu</b-button>
        <em slot="footer"> Location: {{ foodOption.type }}</em>
      </b-card>
    </div>
    </b-card-group>

    </div>
    <div>
      <b-button variant="outline-success" size="lg" class="mt-2 mb-3 mx-3" @click="getPreviousFoodOptions(todaysFoodOptions.date)" title="... is gone!">Previous</b-button>
      <b-button variant="outline-success" size="lg" class="mt-2 mb-3 mx-3" @click="getNextFoodOptions(todaysFoodOptions.date)" title="... isn't here yet!">Next</b-button>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  export default {
    data () {
      return {
        todaysFoodOptions: this.getTodaysFoodOptions(),
        now: this.getNow()
      }
    },
    methods: {
//      created () {
//        setInterval(() => this.now = new Date, 1000 * 60)
//      },
      getNow () {
        let nowDate = new Date()
//        nowDate.setUTCHours(0,0,0,0)
//        console.log(nowDate)
//        nowDate.setHours(0)
//        console.log(nowDate)
//        nowDate.setMinutes(0)
//        nowDate.setSeconds(0)
//        nowDate.setMilliseconds(0)
        this.now = nowDate
        return nowDate
      },
      getTodaysFoodOptions () {
        this.todaysFoodOptions = this.getTodaysFoodOptionsFromAPI('today')
      },
      getPreviousFoodOptions (dateString) {
        let currentDate = dateString.split('-')
        let previousDate = currentDate[0] + '-' + currentDate[1] + '-' + (parseInt(currentDate[currentDate.length - 1]) - 1)
        console.log(currentDate)
        this.todaysFoodOptions = this.getTodaysFoodOptionsFromAPI(previousDate)
      },
      getNextFoodOptions (dateString) {
        let currentDate = dateString.split('-')
        let nextDate = currentDate[0] + '-' + currentDate[1] + '-' + (parseInt(currentDate[currentDate.length - 1]) + 1)
        console.log(currentDate)
        this.todaysFoodOptions = this.getTodaysFoodOptionsFromAPI(nextDate)
      },
      getTodaysFoodOptionsFromAPI (day) {
        let path = '/api/' + day
        axios.get(path)
          .then(response => {
            this.todaysFoodOptions = response.data
          })
          .catch(error => {
            console.log('ERROR!!!!!!!!!!!')
            console.log(error)
          })
      }
    }
  }
</script>

