<template>
  <div>
    <h1>Nom Track</h1>
    <h4>Your one stop shop for everything lunch around the Howard Hughes Center in Los Angeles</h4>
    <h4 class="text-info font-weight-bold">{{ todaysFoodOptions.date}}</h4>
    <h5 class="text-success font-italic">You have xx mins to get food... gogogo</h5>
    <div class="mt-3">
      <b-card-group deck class="mb-3 mx-auto d-flex justify-content-center">

    <div v-for="foodOption in todaysFoodOptions.food_sources">
      <b-card :title="foodOption.name"
              img-src="https://lorempixel.com/600/300/food/5/"
              img-alt="Image"
              img-top
              tag="article"
              style="max-width: 24rem;"
              class="mb-2">
        <div class="card-text">
          {{ foodOption.yelp_info.cost }}
        </div>
        <div v-if="foodOption.yelp_info.rating" class="card-text">
          Yelp Rating: {{ foodOption.yelp_info.rating }}
        </div>
        <div v-if="foodOption.yelp_info.number_of_reviews" class="card-text">
          # of Yelp Reviews: {{ foodOption.yelp_info.number_of_reviews }}
        </div>
        <b-button class="mt-2 mb-2" :href="foodOption.menu" variant="primary">Menu</b-button>
        <em slot="footer"> Location: {{ foodOption.type }}</em>
      </b-card>
    </div>
    </b-card-group>

    </div>
    <div>
      <b-button variant="outline-success" size="lg" class="mt-3 mb-3 mx-3" @click="getPreviousFoodOptions(todaysFoodOptions.date)" title="... is gone!">Previous</b-button>
      <b-button variant="outline-success" size="lg" class="mt-3 mb-3 mx-3" @click="getNextFoodOptions(todaysFoodOptions.date)" title="... isn't here yet!">Next</b-button>
    </div>
  </div>
</template>

<script>
  import axios from 'axios'
  export default {
    data () {
      return {
        todaysFoodOptions: this.getTodaysFoodOptions(),
        now: new Date()
      }
    },
    methods: {
//      created () {
//        setInterval(() => this.now = new Date, 1000 * 60)
//      },
//      getFoodImage () {
//        const path = `https://lorempixel.com/600/300/food/`
//        axios.get(path)
//          .then(response => {
//            console.log('Food Image ====')
//            console.log(response)
//            this.foodImage = response
//          })
//          .catch(error => {
//            console.log('ERROR!!!!!!!!!!!')
//            console.log(error)
//          })
//      },
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
        let path = `http://localhost:5000/api/` + day
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

